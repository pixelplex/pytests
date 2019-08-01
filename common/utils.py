# -*- coding: utf-8 -*-
import datetime
import math
import time
from copy import deepcopy

from fixtures.base_fixtures import get_random_valid_asset_name
from project import BLOCK_RELEASE_INTERVAL, GENESIS, BLOCKS_NUM_TO_WAIT


class Utils(object):

    def __init__(self):
        super().__init__()
        self.waiting_time_result = 0

    @staticmethod
    def add_balance_for_operations(base_test, account, operation, database_api_id, operation_count=1, transfer_amount=0,
                                   only_in_history=False, get_only_fee=True, log_broadcast=False):
        if only_in_history:
            transfer_amount = operation_count * transfer_amount
        if get_only_fee:
            transfer_amount = 0
        amount = operation_count * base_test.get_required_fee(operation, database_api_id)[0]["amount"] + transfer_amount
        transfer_amount_for_pay_fee_op = base_test.echo_ops.get_transfer_operation(echo=base_test.echo,
                                                                                   from_account_id=base_test.echo_acc0,
                                                                                   to_account_id=account, amount=amount)
        collected_operation = base_test.collect_operations(transfer_amount_for_pay_fee_op, database_api_id)
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
                        value_asset_id="1.3.0", supported_asset_id=None, need_broadcast_result=False,
                        log_broadcast=False):
        operation = base_test.echo_ops.get_create_contract_operation(echo=base_test.echo, registrar=registrar,
                                                                     bytecode=contract_bytecode,
                                                                     value_amount=value_amount,
                                                                     value_asset_id=value_asset_id,
                                                                     supported_asset_id=supported_asset_id)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            temp_operation[1]["registrar"] = base_test.echo_acc0
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               transfer_amount=value_amount,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
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
                                            contract_id, operation_count=1, get_only_fee=False, log_broadcast=False):
        operation = base_test.echo_ops.get_call_contract_operation(echo=base_test.echo, registrar=registrar,
                                                                   bytecode=method_bytecode, callee=contract_id)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               operation_count=operation_count,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
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
                                    get_only_fee=False, log_broadcast=False):
        add_balance_operation = 0
        operation = base_test.echo_ops.get_transfer_operation(echo=base_test.echo, from_account_id=account_1,
                                                              to_account_id=account_2, amount=transfer_amount,
                                                              amount_asset_id=amount_asset_id)
        if account_1 != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            temp_operation[1]["from_account_id"] = base_test.echo_acc0
            broadcast_result = self.add_balance_for_operations(base_test, account_1, temp_operation, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               operation_count=operation_count,
                                                               only_in_history=only_in_history,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
            add_balance_operation = 1
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
                                               get_only_fee=False, log_broadcast=False):
        operation = base_test.echo_ops.get_transfer_to_address_operation(echo=base_test.echo, from_account_id=account_1,
                                                                         to_address=to_address, amount=transfer_amount,
                                                                         amount_asset_id=amount_asset_id)
        if account_1 != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            temp_operation[1]["from_account_id"] = base_test.echo_acc0
            broadcast_result = self.add_balance_for_operations(base_test, account_1, temp_operation, database_api_id,
                                                               transfer_amount=transfer_amount,
                                                               operation_count=operation_count,
                                                               get_only_fee=get_only_fee,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
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
        operation = base_test.echo_ops.get_account_address_create_operation(echo=base_test.echo, owner=registrar,
                                                                            label=label)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               operation_count=operation_count,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
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
        operation = base_test.echo_ops.get_withdraw_eth_operation(echo=base_test.echo, account=registrar,
                                                                  eth_addr=eth_addr, value=value)
        if registrar != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, registrar, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: withdraw ethereum from '{}' account is not performed, response:\n{}".format(registrar,
                                                                                                    broadcast_result))
        return broadcast_result

    def get_eth_address(self, base_test, account_id, database_api_id, temp_count=0):
        temp_count += 1
        response_id = base_test.send_request(base_test.get_request("get_eth_address", [account_id]), database_api_id)
        response = base_test.get_response(response_id)
        if response["result"]:
            return response
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
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

    def get_eth_balance(self, base_test, account_id, database_api_id, previous_balance=None, temp_count=0):
        temp_count += 1
        current_balance = self.get_account_balances(base_test, account_id, database_api_id, base_test.eth_asset)[
            "amount"]
        if previous_balance is None and current_balance != 0:
            return current_balance
        if previous_balance and previous_balance != current_balance:
            return current_balance
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
            return self.get_eth_balance(base_test, account_id, database_api_id, previous_balance=previous_balance,
                                        temp_count=temp_count)
        if previous_balance:
            raise Exception("Ethereum balance of '{}' account not updated. Waiting time result='{}'"
                            "".format(account_id, self.waiting_time_result))
        raise Exception(
            "No ethereum balance of '{}' account. Waiting time result='{}'".format(account_id,
                                                                                   self.waiting_time_result))

    @staticmethod
    def cancel_all_subscriptions(base_test, database_api_id):
        response_id = base_test.send_request(base_test.get_request("cancel_all_subscriptions"), database_api_id)
        response = base_test.get_response(response_id)
        if "result" not in response or response["result"] is not None:
            raise Exception("Can't cancel all cancel_all_subscriptions, got:\n{}".format(str(response)))

    def get_updated_address_balance_in_eth_network(self, base_test, account_address, previous_balance, currency="ether",
                                                   temp_count=0):
        temp_count += 1
        current_balance = base_test.eth_trx.get_address_balance_in_eth_network(base_test.web3, account_address,
                                                                               currency=currency)
        if previous_balance != current_balance:
            return current_balance
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
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

    def perform_vesting_balance_create_operation(self, base_test, creator, owner, amount, database_api_id,
                                                 amount_asset_id="1.3.0", begin_timestamp="1970-01-01T00:00:00",
                                                 cliff_seconds=0, duration_seconds=0, log_broadcast=False):
        operation = base_test.echo_ops.get_vesting_balance_create_operation(echo=base_test.echo, creator=creator,
                                                                            owner=owner, amount=amount,
                                                                            amount_asset_id=amount_asset_id,
                                                                            begin_timestamp=begin_timestamp,
                                                                            vesting_cliff_seconds=cliff_seconds,
                                                                            vesting_duration_seconds=duration_seconds)
        if creator != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, creator, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: vesting balance of '{}' account is not withdrawn, response:\n{}".format(owner,
                                                                                                broadcast_result))
        return broadcast_result

    def perform_vesting_balance_withdraw_operation(self, base_test, vesting_balance, owner, amount, database_api_id,
                                                   amount_asset_id="1.3.0", log_broadcast=False):
        operation = base_test.echo_ops.get_vesting_balance_withdraw_operation(echo=base_test.echo,
                                                                              vesting_balance=vesting_balance,
                                                                              owner=owner, amount=amount,
                                                                              amount_asset_id=amount_asset_id)
        if owner != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, owner, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: vesting balance of '{}' account is not withdrawn, response:\n{}".format(owner,
                                                                                                broadcast_result))
        return broadcast_result

    @staticmethod
    def set_datetime_variable(dt, year=0, month=0, day=0, hours=0, minutes=0, seconds=0):
        ts = time.mktime(datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S").timetuple())
        ts = ts + seconds + minutes * 60 + hours * 3600 + day * 86400 + month * 2592000 + year * 31104000
        ts = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")
        return ts

    def get_account_history_operations(self, base_test, account_id, operation_id, history_api_id, limit, start="1.10.0",
                                       stop="1.10.0", temp_count=0):
        temp_count += 1
        params = [account_id, operation_id, start, stop, limit]
        response_id = base_test.send_request(base_test.get_request("get_account_history_operations", params),
                                             history_api_id)
        # todo: remove debug_mode and error block. Bug: "ECHO-700"
        response = base_test.get_response(response_id, debug_mode=True)
        if "error" in response:
            if temp_count <= BLOCKS_NUM_TO_WAIT:
                base_test.set_timeout_wait(wait_block_count=1, print_log=False)
                self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
                return self.get_account_history_operations(base_test, account_id, operation_id, history_api_id,
                                                           start=start, limit=limit, stop=stop, temp_count=temp_count)
        if len(response["result"]) == limit:
            return response
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
            return self.get_account_history_operations(base_test, account_id, operation_id, history_api_id,
                                                       start=start, limit=limit, stop=stop, temp_count=temp_count)
        raise Exception(
            "No needed operation (id='{}') in '{}' account history. "
            "Waiting time result='{}'".format(operation_id, account_id, self.waiting_time_result))

    def perform_contract_fund_pool_operation(self, base_test, sender, contract, value_amount, database_api_id,
                                             value_asset_id="1.3.0", log_broadcast=False):
        operation = base_test.echo_ops.get_contract_fund_pool_operation(echo=base_test.echo, sender=sender,
                                                                        contract=contract, value_amount=value_amount,
                                                                        value_asset_id=value_asset_id)
        if sender != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, sender, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: fund pool from '{}' account is not performed, response:\n{}".format(sender, broadcast_result))
        return broadcast_result

    def perform_contract_whitelist_operation(self, base_test, sender, contract, database_api_id, add_to_whitelist=None,
                                             remove_from_whitelist=None, add_to_blacklist=None,
                                             remove_from_blacklist=None, log_broadcast=False):
        operation = base_test.echo_ops.get_contract_whitelist_operation(echo=base_test.echo, sender=sender,
                                                                        contract=contract,
                                                                        add_to_whitelist=add_to_whitelist,
                                                                        remove_from_whitelist=remove_from_whitelist,
                                                                        add_to_blacklist=add_to_blacklist,
                                                                        remove_from_blacklist=remove_from_blacklist)
        if sender != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, sender, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: fund pool from '{}' account is not performed, response:\n{}".format(sender, broadcast_result))
        return broadcast_result

    def perform_account_upgrade_operation(self, base_test, account_id, database_api_id, lifetime=True,
                                          log_broadcast=False):
        operation = base_test.echo_ops.get_account_upgrade_operation(base_test.echo, account_to_upgrade=account_id,
                                                                     upgrade_to_lifetime_member=lifetime)
        if account_id != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account_id, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
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
        operation = base_test.echo_ops.get_committee_member_create_operation(echo=base_test.echo,
                                                                             committee_member_account=account_id,
                                                                             eth_address=eth_address, url="test_url")
        if account_id != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account_id, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception(
                "Error: '{}' account did not become new committee member, response:\n{}".format(account_id,
                                                                                                broadcast_result))
        return broadcast_result

    def perform_account_update_operation(self, base_test, account_id, account_info, database_api_id,
                                         log_broadcast=False):
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
        if account_id != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account_id, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception(
                "Error: '{}' account did not update, response:\n{}".format(account_id, broadcast_result))
        return broadcast_result

    def perform_contract_update_operation(self, base_test, sender, contract, database_api_id, new_owner=None,
                                          log_broadcast=False):
        operation = base_test.echo_ops.get_contract_update_operation(echo=base_test.echo, sender=sender,
                                                                     contract=contract, new_owner=new_owner)
        if sender != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, sender, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))

        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Error: '{}' contract did not update, response:\n{}".format(contract, broadcast_result))
        return broadcast_result

    def perform_register_erc20_token_operation(self, base_test, account, eth_addr, name, symbol, database_api_id,
                                               decimals=0, log_broadcast=False):
        if eth_addr[:2] == "0x":
            eth_addr = eth_addr[2:]
        operation = base_test.echo_ops.get_register_erc20_token_operation(echo=base_test.echo, account=account,
                                                                          eth_addr=eth_addr, name=name, symbol=symbol,
                                                                          decimals=decimals)
        if account != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: ERC20 token did not register, response:\n{}".format(broadcast_result))
        return broadcast_result

    def perform_withdraw_erc20_token_operation(self, base_test, account, to, erc20_token, value, database_api_id,
                                               log_broadcast=False):
        if to[:2] == "0x":
            to = to[2:]
        operation = base_test.echo_ops.get_withdraw_erc20_token_operation(echo=base_test.echo, account=account,
                                                                          to=to, erc20_token=erc20_token, value=value)
        if account != base_test.echo_acc0:
            temp_operation = deepcopy(operation)
            broadcast_result = self.add_balance_for_operations(base_test, account, temp_operation, database_api_id,
                                                               log_broadcast=log_broadcast)
            if not base_test.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(broadcast_result))
        collected_operation = base_test.collect_operations(operation, database_api_id)
        broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                        log_broadcast=log_broadcast)
        if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Error: ERC20 token did not withdrew, response:\n{}".format(broadcast_result))
        return broadcast_result

    def get_erc20_account_deposits(self, base_test, account_id, database_api_id, previous_account_deposits=None,
                                   temp_count=0):
        temp_count += 1
        response_id = base_test.send_request(base_test.get_request("get_erc20_account_deposits", [account_id]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        if response["result"] and response["result"] != previous_account_deposits:
            return response
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
            return self.get_erc20_account_deposits(base_test, account_id, database_api_id,
                                                   previous_account_deposits=previous_account_deposits,
                                                   temp_count=temp_count)
        raise Exception(
            "No needed '{}' account erc20 deposits. Waiting time result='{}'".format(account_id,
                                                                                     self.waiting_time_result))

    def get_erc20_account_withdrawals(self, base_test, account_id, database_api_id, previous_account_withdrawals=None,
                                      temp_count=0):
        temp_count += 1
        response_id = base_test.send_request(base_test.get_request("get_erc20_account_withdrawals", [account_id]),
                                             database_api_id)
        response = base_test.get_response(response_id)
        if response["result"] and response["result"] != previous_account_withdrawals:
            return response
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
            return self.get_erc20_account_withdrawals(base_test, account_id, database_api_id,
                                                      previous_account_withdrawals=previous_account_withdrawals,
                                                      temp_count=temp_count)
        raise Exception(
            "No needed '{}' account erc20 withdrawals. Waiting time result='{}'".format(account_id,
                                                                                        self.waiting_time_result))

    def get_updated_account_erc20_balance_in_eth_network(self, base_test, contract_instance, eth_account,
                                                         previous_balance, temp_count=0):
        temp_count += 1
        current_balance = base_test.eth_trx.get_balance_of(contract_instance, eth_account)
        if previous_balance != current_balance:
            return current_balance
        if temp_count <= BLOCKS_NUM_TO_WAIT:
            base_test.set_timeout_wait(wait_block_count=1, print_log=False)
            self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
            return self.get_updated_account_erc20_balance_in_eth_network(base_test, contract_instance, eth_account,
                                                                         previous_balance, temp_count=temp_count)
        raise Exception(
            "ERC20 balance of '{}' account not updated. Waiting time result='{}'".format(eth_account,
                                                                                         self.waiting_time_result))
