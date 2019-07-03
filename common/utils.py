# -*- coding: utf-8 -*-
import math

from fixtures.base_fixtures import get_random_valid_asset_name
from project import BLOCK_RELEASE_INTERVAL, GENESIS


class Utils(object):

    def __init__(self):
        super().__init__()
        self.waiting_time_result = 0
        self.block_count = 10

    @staticmethod
    def add_balance_for_operations(base_test, account, database_api_id, contract_bytecode=None, contract_value=0,
                                   method_bytecode=None, callee="1.14.0", transfer_amount=None, to_address=None,
                                   transfer_asset_id=None, asset_name=None, operation_count=1, label=None,
                                   lifetime=None, eth_address=None, update_account=None, eth_addr=None,
                                   vesting_balance=None, fee_pool=None, only_in_history=False, log_broadcast=False):
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
        if vesting_balance is not None:
            operation = base_test.echo_ops.get_operation_json("vesting_balance_withdraw_operation", example=True)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if lifetime is not None:
            operation = base_test.echo_ops.get_account_upgrade_operation(echo=base_test.echo,
                                                                         account_to_upgrade=account,
                                                                         upgrade_to_lifetime_member=lifetime)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if eth_address is not None:
            operation = base_test.echo_ops.get_committee_member_create_operation(echo=base_test.echo,
                                                                                 committee_member_account=account,
                                                                                 eth_address=eth_address)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if update_account is not None:
            operation = base_test.echo_ops.get_operation_json("get_account_update_operation", example=True)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if eth_addr is not None:
            operation = base_test.echo_ops.get_operation_json("withdraw_eth_operation", example=True)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        if fee_pool is not None:
            operation = base_test.echo_ops.get_operation_json("contract_fund_pool_operation", example=True)
            amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"]
        operation = base_test.echo_ops.get_transfer_operation(echo=base_test.echo, from_account_id=base_test.echo_acc0,
                                                              to_account_id=account, amount=amount)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        return base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                            log_broadcast=log_broadcast)

    def get_nonexistent_asset_id(self, base_test, database_api_id, symbol="", list_asset_ids=None, return_symbol=False):
        if list_asset_ids is None:
            list_asset_ids = []
        max_limit = 100
        response_id = base_test.send_request(base_test.get_request("list_assets", [symbol, max_limit]), database_api_id)
        response = base_test.get_response(response_id)
        for asset in response["result"]:
            list_asset_ids.append(asset["id"])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_asset_id(base_test, database_api_id, symbol=list_asset_ids[-1],
                                                 list_asset_ids=list_asset_ids, return_symbol=return_symbol)
        sorted_list_asset_ids = sorted(list_asset_ids, key=base_test.get_value_for_sorting_func)
        asset_id = "{}{}".format(base_test.get_object_type(base_test.echo.config.object_types.ASSET),
                                 str(int(sorted_list_asset_ids[-1][4:]) + 1))
        if return_symbol:
            return asset_id, symbol
        return asset_id

    def get_nonexistent_asset_symbol(self, base_test, database_api_id, symbol="",
                                     list_asset_symbols=None):
        if list_asset_symbols is None:
            list_asset_symbols = []
        max_limit = 100
        response_id = base_test.send_request(base_test.get_request("list_assets", [symbol, max_limit]), database_api_id)
        response = base_test.get_response(response_id)
        for asset in response["result"]:
            list_asset_symbols.append(asset["symbol"])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_asset_symbol(base_test, database_api_id, symbol=list_asset_symbols[-1],
                                                     list_asset_symbols=list_asset_symbols)
        nonexistent_asset_symbol = list_asset_symbols[0]
        while nonexistent_asset_symbol in list_asset_symbols:
            nonexistent_asset_symbol = get_random_valid_asset_name()
        return nonexistent_asset_symbol

    def get_nonexistent_account_name_for_lookup(self, base_test, database_api_id, lower_bound_name="",
                                                list_account_names=None):
        if list_account_names is None:
            list_account_names = []
        max_limit = 1000
        response_id = base_test.send_request(base_test.get_request("lookup_accounts", [lower_bound_name, max_limit]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        for account in response["result"]:
            list_account_names.append(account[0])
        if len(response["result"]) == max_limit:
            return self.get_nonexistent_account_name_for_lookup(base_test, database_api_id,
                                                                lower_bound_name=list_account_names[-1],
                                                                list_account_names=list_account_names)

        account_names_count = len(list_account_names)
        result_lower_bound_name = list_account_names[len(list_account_names) // max_limit * max_limit] \
            if account_names_count > 1000 else lower_bound_name
        result_limit = account_names_count % max_limit + 1 if account_names_count > 1000 \
            else account_names_count + 1

        return result_lower_bound_name, result_limit

    def get_contract_id(self, base_test, registrar, contract_bytecode, database_api_id, value_amount=0,
                        value_asset_id="1.3.0", supported_asset_id=None, operation_count=1, need_broadcast_result=False,
                        log_broadcast=False):
        if registrar != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, registrar, database_api_id,
                                                               contract_bytecode=contract_bytecode,
                                                               contract_value=value_amount,
                                                               operation_count=operation_count)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_create_contract_operation(echo=base_test.echo, registrar=registrar,
                                                                     bytecode=contract_bytecode,
                                                                     value_amount=value_amount,
                                                                     value_asset_id=value_asset_id,
                                                                     supported_asset_id=supported_asset_id)
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
        if account_1 != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, account_1, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               to_address=to_address,
                                                               transfer_asset_id=amount_asset_id,
                                                               operation_count=operation_count)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_transfer_to_address_operation(echo=base_test.echo, from_account_id=account_1,
                                                                         to_address=to_address, amount=transfer_amount,
                                                                         amount_asset_id=amount_asset_id)
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

    @staticmethod
    def check_accounts_have_initial_balances(accounts):
        initial_accounts = {account["name"]: account["echorand_key"] for account in GENESIS["initial_accounts"]
                            if account["name"] in accounts}
        initial_balances_keys = [balance["owner"] for balance in GENESIS["initial_balances"]]
        initial_balances_keys = list(filter(lambda balance: balance in initial_accounts.values(),
                                            initial_balances_keys))
        if len(initial_balances_keys) < len(accounts):
            return False
        return True

    @staticmethod
    def get_account_id(base_test, account_names, account_keys, database_api_id, signer=None,
                       need_operations=False, log_broadcast=False):
        if signer is None:
            signer = base_test.echo_acc0
        if type(account_names) is str:
            operation = base_test.echo_ops.get_account_create_operation(echo=base_test.echo, name=account_names,
                                                                        active_key_auths=account_keys[1],
                                                                        echorand_key=account_keys[1],
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
                                                                        echorand_key=account_keys[i][1],
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
    def get_asset_id(base_test, symbol, database_api_id, need_operation=False, log_broadcast=False):
        params = [symbol, 1]
        response_id = base_test.send_request(base_test.get_request("list_assets", params), database_api_id, )
        response = base_test.get_response(response_id)
        if not response["result"] or response["result"][0]["symbol"] != symbol:
            operation = base_test.echo_ops.get_asset_create_operation(echo=base_test.echo, issuer=base_test.echo_acc0,
                                                                      symbol=symbol)
            collected_operation = base_test.collect_operations(operation, database_api_id)
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            asset_id = base_test.get_operation_results_ids(broadcast_result)
            if need_operation:
                return asset_id, collected_operation
            return asset_id
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
                                                 operation_count=1, log_broadcast=False):
        if registrar != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, registrar, database_api_id,
                                                               operation_count=operation_count, label=label)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_account_address_create_operation(echo=base_test.echo, owner=registrar,
                                                                            label=label)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        if operation_count == 1:
            broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                            log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Error: new address of '{}' account is not created, "
                                "response:\n{}".format(registrar, broadcast_result))
            return broadcast_result
        list_operations = []
        for i in range(operation_count):
            list_operations.append(collected_operation)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                        log_broadcast=log_broadcast)
        return broadcast_result

    @staticmethod
    def perform_generate_eth_address_operation(base_test, registrar, database_api_id, log_broadcast=False):
        operation = base_test.echo_ops.get_generate_eth_address_operation(echo=base_test.echo, account=registrar)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: new eth address of '{}' account is not created, response:\n{}".format(registrar,
                                                                                              broadcast_result))
        return broadcast_result

    def perform_withdraw_eth_operation(self, base_test, registrar, eth_addr, value, database_api_id,
                                       log_broadcast=False):
        if eth_addr[:2] == "0x":
            eth_addr = eth_addr[2:]
        if registrar != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, registrar, database_api_id, eth_addr=eth_addr)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_withdraw_eth_operation(echo=base_test.echo, account=registrar,
                                                                  eth_addr=eth_addr, value=value)
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
            return self.get_eth_address(base_test, account_id, database_api_id, temp_count=temp_count)
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
            return self.get_eth_balance(base_test, account_id, database_api_id, temp_count=temp_count)
        raise Exception(
            "No ethereum balance of '{}' account. Waiting time result='{}'".format(account_id,
                                                                                   self.waiting_time_result))

    @staticmethod
    def cancel_all_subscriptions(base_test, database_api_id):
        response_id = base_test.send_request(base_test.get_request("cancel_all_subscriptions"), database_api_id)
        response = base_test.get_response(response_id)
        if response["result"] is not None:
            raise Exception("Can't cancel all cancel_all_subscriptions, got:\n{}".format(str(response)))

    def get_updated_address_balance_in_eth_network(self, base_test, account_address, previous_balance, currency="ether",
                                                   temp_count=0, timeout=BLOCK_RELEASE_INTERVAL):
        temp_count += 1
        current_balance = base_test.eth_trx.get_address_balance_in_eth_network(base_test.web3, account_address,
                                                                               currency=currency)
        if previous_balance != current_balance:
            return current_balance
        if temp_count <= self.block_count:
            base_test.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_updated_address_balance_in_eth_network(base_test, account_address, previous_balance,
                                                                   currency=currency, temp_count=temp_count)
        raise Exception(
            "Ethereum balance of '{}' account not updated. Waiting time result='{}'".format(account_address,
                                                                                            self.waiting_time_result))

    @staticmethod
    def convert_ethereum_to_eeth(value):
        return math.floor((value * 10 ** 6))

    @staticmethod
    def convert_eeth_to_currency(value, currency="wei"):
        if currency == "wei":
            return value * 10 ** 12
        if currency == "ether":
            return value / 10 ** 6

    def perform_vesting_balance_withdraw_operation(self, base_test, vesting_balance, owner, amount, database_api_id,
                                                   log_broadcast=False):
        if owner != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, owner, database_api_id,
                                                               vesting_balance=vesting_balance)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_vesting_balance_withdraw_operation(echo=base_test.echo,
                                                                              vesting_balance=vesting_balance,
                                                                              owner=owner, amount=amount)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: vesting balance of '{}' account is not withdrawn, response:\n{}".format(owner,
                                                                                                broadcast_result))
        return broadcast_result

    def get_account_history_operations(self, base_test, account_id, operation_id, history_api_id, limit, start="1.10.0",
                                       stop="1.10.0", temp_count=0, timeout=BLOCK_RELEASE_INTERVAL):
        temp_count += 1
        # todo: remove timeout_wait. Bug: "ECHO-700"
        base_test.set_timeout_wait(BLOCK_RELEASE_INTERVAL * 2)
        params = [account_id, operation_id, start, stop, limit]
        response_id = base_test.send_request(base_test.get_request("get_account_history_operations", params),
                                             history_api_id)
        response = base_test.get_response(response_id)
        if len(response["result"]) == limit:
            return response
        if temp_count <= self.block_count:
            base_test.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_account_history_operations(base_test, account_id, operation_id, history_api_id,
                                                       start=start, limit=limit, stop=stop, temp_count=temp_count)
        raise Exception(
            "No needed operation (id='{}') in '{}' account history. "
            "Waiting time result='{}'".format(operation_id, account_id, self.waiting_time_result))

    def perform_contract_fund_pool_operation(self, base_test, sender, contract, value_amount, database_api_id,
                                             value_asset_id="1.3.0", fee_pool=True, log_broadcast=False):
        if sender != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, sender, database_api_id,
                                                               fee_pool=fee_pool)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_contract_fund_pool_operation(echo=base_test.echo, sender=sender,
                                                                        contract=contract, value_amount=value_amount,
                                                                        value_asset_id=value_asset_id)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: fund pool from '{}' account is not performed, response:\n{}".format(sender, broadcast_result))
        return broadcast_result

    def perform_account_upgrade_operation(self, base_test, account_id, database_api_id, lifetime=True,
                                          log_broadcast=False):
        if account_id != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, account_id, database_api_id,
                                                               lifetime=lifetime)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_account_upgrade_operation(base_test.echo, account_to_upgrade=account_id,
                                                                     upgrade_to_lifetime_member=lifetime)
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: '{}' account did not become lifetime member, response:\n{}".format(account_id,
                                                                                           broadcast_result))
        return broadcast_result

    def perform_committee_member_create_operation(self, base_test, account_id, eth_address, database_api_id,
                                                  log_broadcast=False):
        if account_id != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, account_id, database_api_id,
                                                               eth_address=eth_address)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        operation = base_test.echo_ops.get_committee_member_create_operation(echo=base_test.echo,
                                                                             committee_member_account=account_id,
                                                                             eth_address=eth_address, url="test_url")
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: '{}' account did not become new committee member, response:\n{}".format(account_id,
                                                                                                broadcast_result))
        return broadcast_result

    def perform_account_update_operation(self, base_test, account_id, account_info, database_api_id,
                                         update_account=True, log_broadcast=False):
        if account_id != base_test.echo_acc0:
            broadcast_result = self.add_balance_for_operations(base_test, account_id, database_api_id,
                                                               update_account=update_account)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        active, echorand_key, options = account_info["active"], account_info["echorand_key"], account_info["options"]
        operation = base_test.echo_ops.get_account_update_operation(echo=base_test.echo, account=account_id,
                                                                    weight_threshold=active["weight_threshold"],
                                                                    account_auths=active["account_auths"],
                                                                    key_auths=active["key_auths"],
                                                                    echorand_key=echorand_key,
                                                                    voting_account=options["voting_account"],
                                                                    delegating_account=options["delegating_account"],
                                                                    num_committee=options["num_committee"],
                                                                    votes=options["votes"])
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: '{}' account did not update, response:\n{}".format(account_id, broadcast_result))
        return broadcast_result
