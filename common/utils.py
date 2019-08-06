# -*- coding: utf-8 -*-
import math

from project import BLOCK_RELEASE_INTERVAL, ETH_CONTRACT_ADDRESS, UNPAID_FEE_METHOD


class Utils(object):

    def __init__(self):
        super().__init__()
        self.waiting_time_result = 0
        self.block_count = 10

    @staticmethod
    def add_balance_for_operations(base_test, account, database_api_id, contract_bytecode=None, contract_value=0,
                                   method_bytecode=None, callee="1.14.0", transfer_amount=None, to_address=None,
                                   transfer_asset_id=None, asset_name=None, operation_count=1, label=None,
                                   only_in_history=False, log_broadcast=False):
        amount = 0
        if contract_bytecode is not None:
            operation = base_test.echo_ops.get_create_contract_operation(echo=base_test.echo, registrar=account,
                                                                         bytecode=contract_bytecode)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0][
                "amount"] + contract_value
        if method_bytecode is not None:
            operation = base_test.echo_ops.get_call_contract_operation(echo=base_test.echo, registrar=account,
                                                                       bytecode=method_bytecode, callee=callee)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if transfer_amount is not None and to_address is None:
            operation = base_test.echo_ops.get_operation_json("transfer_operation", example=True)
            operation[1]["amount"].update({"amount": transfer_amount, "asset_id": transfer_asset_id})
            fee = base_test.get_required_fee(operation, database_api_id)[0]["amount"]
            if only_in_history:
                amount = operation_count * transfer_amount
            amount = amount + (operation_count * fee)
        if to_address is not None:
            operation = base_test.echo_ops.get_operation_json("transfer_to_address_operation", example=True)
            operation[1]["amount"].update({"amount": transfer_amount, "asset_id": transfer_asset_id})
            fee = base_test.get_required_fee(operation, database_api_id)[0]["amount"]
            amount = amount + (operation_count * fee)
        if asset_name is not None:
            operation = base_test.echo_ops.get_operation_json("asset_create_operation", example=True)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if label is not None:
            operation = base_test.echo_ops.get_account_address_create_operation(echo=base_test.echo, owner=account,
                                                                                label=label)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        operation = base_test.echo_ops.get_transfer_operation(echo=base_test.echo,
                                                              from_account_id=base_test.echo_acc0,
                                                              to_account_id=account, amount=amount)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        return base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                            log_broadcast=log_broadcast)

    def get_nonexistent_asset_id(self, base_test, database_api_id, symbol=""):
        max_limit = 100
        list_asset_ids = []
        response_id = base_test.send_request(base_test.get_request("list_assets", [symbol, max_limit]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        for i in range(len(response["result"])):
            list_asset_ids.append(response["result"][i]["id"])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_asset_id(base_test, database_api_id,
                                                 symbol=response["result"][-1]["symbol"])
        sorted_list_asset_ids = sorted(list_asset_ids, key=base_test.get_value_for_sorting_func)
        return "{}{}".format(base_test.get_object_type(base_test.echo.config.object_types.ASSET),
                             str(int(sorted_list_asset_ids[-1][4:]) + 1))

    def get_contract_id(self, base_test, registrar, contract_bytecode, database_api_id, value_amount=0,
                        operation_count=1, need_broadcast_result=False, log_broadcast=False):
        if registrar != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, registrar, database_api_id,
                                                               contract_bytecode=contract_bytecode,
                                                               contract_value=value_amount,
                                                               operation_count=operation_count)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_create_contract_operation(echo=base_test.echo, registrar=registrar,
                                                                     bytecode=contract_bytecode,
                                                                     value_amount=value_amount)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        contract_result = base_test.get_operation_results_ids(broadcast_result)
        response_id = base_test.send_request(base_test.get_request("get_contract_result", [contract_result]),
                                             database_api_id)
        contract_id_16 = base_test.get_trx_completed_response(response_id)
        if not need_broadcast_result:
            return base_test.get_contract_id(contract_id_16)
        return {"contract_id": base_test.get_contract_id(contract_id_16), "broadcast_result": broadcast_result}

    def perform_contract_transfer_operation(self, base_test, registrar, method_bytecode, database_api_id,
                                            contract_id, operation_count=1, log_broadcast=False):
        if registrar != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, registrar, database_api_id,
                                                               method_bytecode=method_bytecode, callee=contract_id,
                                                               operation_count=operation_count)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_call_contract_operation(echo=base_test.echo, registrar=registrar,
                                                                   bytecode=method_bytecode, callee=contract_id)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            return broadcast_result
        list_operations = []
        for i in range(operation_count):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    def perform_transfer_operations(self, base_test, account_1, account_2, database_api_id, transfer_amount=1,
                                    operation_count=1, only_in_history=False, amount_asset_id="1.3.0",
                                    log_broadcast=False):
        add_balance_operation = 0
        if account_1 != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, account_1, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               transfer_asset_id=amount_asset_id,
                                                               operation_count=operation_count,
                                                               only_in_history=only_in_history)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
            add_balance_operation = 1
        operation = base_test.echo_ops.get_transfer_operation(echo=base_test.echo, from_account_id=account_1,
                                                              to_account_id=account_2, amount=transfer_amount,
                                                              amount_asset_id=amount_asset_id)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            return broadcast_result
        list_operations = []
        for i in range(operation_count - add_balance_operation):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    def perform_transfer_to_address_operations(self, base_test, account_1, to_address, database_api_id,
                                               transfer_amount=1, amount_asset_id="1.3.0", operation_count=1,
                                               log_broadcast=False):
        add_balance_operation = 0
        if account_1 != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, account_1, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               to_address=to_address,
                                                               transfer_asset_id=amount_asset_id,
                                                               operation_count=operation_count)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
            add_balance_operation = 1
        operation = base_test.echo_ops.get_transfer_to_address_operation(echo=base_test.echo, from_account_id=account_1,
                                                                         to_address=to_address, amount=transfer_amount,
                                                                         amount_asset_id=amount_asset_id)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            return broadcast_result
        list_operations = []
        for i in range(operation_count - add_balance_operation):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    @staticmethod
    def get_account_id(base_test, account_names, account_keys, database_api_id, signer=None,
                       need_operations=False, log_broadcast=False):
        if signer is None:
            signer = base_test.echo_acc0
        if type(account_names) is str:
            operation = base_test.echo_ops.get_account_create_operation(echo=base_test.echo, name=account_names,
                                                                        active_key_auths=account_keys[1],
                                                                        ed_key=account_keys[1],
                                                                        options_memo_key=account_keys[2],
                                                                        registrar=signer, signer=signer)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Default accounts are not created")
            account_id = base_test.get_operation_results_ids(broadcast_result)
            if need_operations:
                return {"account_id": account_id, "operation": collected_operation}
            return account_id
        list_operations = []
        for i in range(len(account_names)):
            operation = base_test.echo_ops.get_account_create_operation(echo=base_test.echo, name=account_names[i],
                                                                        active_key_auths=account_keys[i][1],
                                                                        ed_key=account_keys[i][1],
                                                                        options_memo_key=account_keys[i][2],
                                                                        registrar=signer, signer=signer)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Default accounts are not created")
        operation_results = base_test.get_operation_results_ids(broadcast_result)
        accounts_ids = []
        for i in range(len(operation_results)):
            accounts_ids.append(operation_results[i][1])
        if need_operations:
            return {"accounts_ids": accounts_ids, "account_names": account_names, "list_operations": list_operations}
        return accounts_ids

    @staticmethod
    def get_asset_id(base_test, symbol, database_api_id, log_broadcast=False):
        params = [symbol, 1]
        response_id = base_test.send_request(base_test.get_request("list_assets", params), database_api_id, )
        response = base_test.get_response(response_id)
        if not response["result"] or response["result"][0]["symbol"] != symbol:
            operation = base_test.echo_ops.get_asset_create_operation(echo=base_test.echo, issuer=base_test.echo_acc0,
                                                                      symbol=symbol)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            return base_test.get_operation_results_ids(broadcast_result)
        return response["result"][0]["id"]

    @staticmethod
    def add_assets_to_account(base_test, value, asset_id, to_account, database_api_id, log_broadcast=False):
        operation = base_test.echo_ops.get_asset_issue_operation(echo=base_test.echo, issuer=base_test.echo_acc0,
                                                                 value_amount=value, value_asset_id=asset_id,
                                                                 issue_to_account=to_account)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: new asset holder '{}' not added, response:\n{}".format(to_account, broadcast_result))
        return broadcast_result

    def perform_account_address_create_operation(self, base_test, registrar, label, database_api_id,
                                                 log_broadcast=False):
        if registrar != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, registrar, database_api_id, label=label)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_account_address_create_operation(echo=base_test.echo, owner=registrar,
                                                                            label=label)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: new address of '{}' account is not created, response:\n{}".format(registrar, broadcast_result))
        return broadcast_result

    @staticmethod
    def perform_generate_eth_address_operation(base_test, registrar, database_api_id, log_broadcast=False):
        operation = base_test.echo_ops.get_generate_eth_address_operation(echo=base_test.echo, account_id=registrar)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: new eth address of '{}' account is not created, response:\n{}".format(registrar,
                                                                                              broadcast_result))
        return broadcast_result

    @staticmethod
    def perform_withdraw_eth_operation_operation(base_test, registrar, eth_addr, value, database_api_id,
                                                 log_broadcast=False):
        operation = base_test.echo_ops.get_withdraw_eth_operation(echo=base_test.echo, acc_id=registrar,
                                                                  eth_addr=eth_addr,
                                                                  value=value)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: withdraw ethereum from '{}' account is not performed, response:\n{}".format(registrar,
                                                                                                    broadcast_result))
        return broadcast_result

    def get_eth_address(self, base_test, account_id, database_api_id, temp_count=0, timeout=BLOCK_RELEASE_INTERVAL):
        temp_count += 1
        response_id = base_test.send_request(base_test.get_request("get_eth_address", [account_id]), database_api_id)
        response = base_test.get_response(response_id)
        if response["result"]:
            return response
        if temp_count <= self.block_count:
            base_test.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_eth_address(base_test, account_id, database_api_id, timeout=timeout)
        raise Exception(
            "No ethereum address of '{}' account. Waiting time result='{}'".format(account_id,
                                                                                   self.waiting_time_result))

    @staticmethod
    def get_account_balances(base_test, account, database_api_id, assets=None):
        if assets is None:
            assets = [base_test.echo_asset]
        elif base_test.validator.is_asset_id(assets):
            assets = [assets]
        params = [account, assets]
        response_id = base_test.send_request(base_test.get_request("get_account_balances", params), database_api_id)
        if len(assets) == 1:
            return base_test.get_response(response_id)["result"][0]
        return base_test.get_response(response_id)["result"]

    def get_eth_balance(self, base_test, account_id, database_api_id, temp_count=0, timeout=BLOCK_RELEASE_INTERVAL):
        temp_count += 1
        ethereum_balance = self.get_account_balances(base_test, account_id, database_api_id, base_test.eth_asset)
        if ethereum_balance["amount"] != 0:
            return ethereum_balance
        if temp_count <= self.block_count:
            base_test.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_eth_balance(base_test, account_id, database_api_id)
        raise Exception(
            "No ethereum balance of '{}' account. Waiting time result='{}'".format(account_id,
                                                                                   self.waiting_time_result))

    @staticmethod
    def cancel_all_subscriptions(base_test, database_api_id):
        response_id = base_test.send_request(base_test.get_request("cancel_all_subscriptions"), database_api_id)
        response = base_test.get_response(response_id)
        if response["result"] is not None:
            raise Exception("Can't cancel all cancel_all_subscriptions, got:\n{}".format(str(response)))

    @staticmethod
    def get_address_balance_in_eth_network(base_test, account_address, currency="ether"):
        return base_test.web3.fromWei(base_test.web3.eth.getBalance(account_address), currency)

    def get_updated_address_balance_in_eth_network(self, base_test, account_address, previous_balance, temp_count=0,
                                                   currency="ether", timeout=BLOCK_RELEASE_INTERVAL):
        temp_count += 1
        current_balance = self.get_address_balance_in_eth_network(base_test, account_address, currency=currency)
        if previous_balance != current_balance:
            return current_balance
        if temp_count <= self.block_count:
            base_test.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_updated_address_balance_in_eth_network(base_test, account_address, previous_balance,
                                                                   currency=currency)
        raise Exception(
            "Ethereum balance of '{}' account not updated. Waiting time result='{}'".format(account_address,
                                                                                            self.waiting_time_result))

    @staticmethod
    def get_unpaid_fee(base_test, account_id, in_ethereum=False):
        method_call_result = base_test.web3.eth.call(
            {
                "to": base_test.web3.toChecksumAddress(ETH_CONTRACT_ADDRESS),
                "data": UNPAID_FEE_METHOD + base_test.get_byte_code_param(account_id)
            }
        )
        if in_ethereum:
            return int(method_call_result.hex()[-64:], 16) / 1e18
        return round(int(method_call_result.hex()[-64:], 16) / 1e12)

    @staticmethod
    def convert_ethereum_to_eeth(value):
        return math.floor((value * 10 ** 6))

    @staticmethod
    def convert_eeth_to_currency(value, currency="wei"):
        if currency == "wei":
            return value * 10 ** 12
        if currency == "ether":
            return value / 10 ** 6
