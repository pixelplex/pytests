# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, require_that_entry, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_fee_pool_balances'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract_fee_pool_balances")
@lcc.suite("Check work of method 'get_contract_fee_pool_balances '", rank=1)
class GetContractFeePoolBalances(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_fee_pool_balances'")
    def method_main_check(self, get_random_integer):
        value_to_pool = get_random_integer

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Get a contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contract'")
        with this_dict(result):
            if check_that("contract pool balance", result, has_length(2)):
                check_that_entry("amount", equal_to(value_to_pool))
                check_that_entry("asset_id", equal_to(self.echo_asset))


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_contract_fee_pool_balances")
@lcc.suite("Positive testing of method 'get_contract_fee_pool_balances'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy()")

    @staticmethod
    def get_random_amount(_to, _from=1):
        return round(random.randrange(_from, _to))

    def get_user_to_pay_fee_amount(self, operation):
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], self.echo_asset]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if not response.get("result")[0].get("user_to_pay"):
            raise Exception("Given operation not contract call. Got required fee: {}".format(str(response)))
        return response.get("result")[0].get("user_to_pay").get("amount")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Add fee pool and call contract using new account with empty balance")
    @lcc.depends_on("DatabaseApi.GetContractFeePoolBalances.GetContractFeePoolBalances.method_main_check")
    def add_fee_pool_to_call_contract(self, get_random_valid_account_name, get_random_integer_up_to_ten):
        new_account = get_random_valid_account_name
        contract_balance = get_random_integer_up_to_ten

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=contract_balance)

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get balances of new account and check that it empty")
        params = [new_account, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]
        with this_dict(account_balance):
            require_that_entry("amount", equal_to(0))
            require_that_entry("asset_id", equal_to(self.echo_asset))

        lcc.set_step("First: add fee pool to perform the call contract 'greet' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=new_account,
                                                              bytecode=self.greet, callee=contract_id)
        needed_fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, needed_fee,
                                                        self.__database_api_identifier)
        lcc.log_info("Added '{}' assets value to '{}' contract fee pool successfully".format(needed_fee, contract_id))

        lcc.set_step("Get a contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        fee_pool_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'. "
                     "Fee pool balance: '{}' assets".format(contract_id, fee_pool_balance))

        lcc.set_step("Call 'greet' method using new account, that don't have any balance")
        user_to_pay_fee = self.get_user_to_pay_fee_amount(operation)
        check_that("'user to pay fee amount'", user_to_pay_fee, equal_to(0))
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get a contract's fee pool balance after contract call")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        updated_fee_pool_balance = self.get_response(response_id)["result"]["amount"]

        lcc.set_step("Check that contract pool balance became empty")
        check_that("'contract pool balance'", updated_fee_pool_balance, equal_to(fee_pool_balance - needed_fee))

        lcc.set_step("Get balances of new account and check that it empty")
        params = [new_account, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]
        with this_dict(account_balance):
            require_that_entry("amount", equal_to(0))
            require_that_entry("asset_id", equal_to(self.echo_asset))

        lcc.set_step("Add echo assets to new_account")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=new_account,
                                                              bytecode=self.get_pennie, callee=contract_id)
        needed_fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account, self.__database_api_identifier,
                                               transfer_amount=needed_fee, log_broadcast=True)

        lcc.set_step("Second: add fee pool using not contract owner to perform the call contract 'get_pennie' method")
        self.utils.perform_contract_fund_pool_operation(self, new_account, contract_id, needed_fee,
                                                        self.__database_api_identifier)
        lcc.log_info("Added '{}' assets value to '{}' contract fee pool successfully".format(needed_fee, contract_id))

        lcc.set_step("Get a contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        fee_pool_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'. "
                     "Fee pool balance: '{}' assets".format(contract_id, fee_pool_balance))

        lcc.set_step("Call 'get_pennie' method using new account, that don't have any balance")
        user_to_pay_fee = self.get_user_to_pay_fee_amount(operation)
        check_that("'user to pay fee amount'", user_to_pay_fee, equal_to(0))
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get a contract's fee pool balance after contract call")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        updated_fee_pool_balance = self.get_response(response_id)["result"]["amount"]

        lcc.set_step("Check that contract pool balance became empty")
        check_that("'contract pool balance'", updated_fee_pool_balance, equal_to(fee_pool_balance - needed_fee))

    @lcc.prop("type", "method")
    @lcc.test("Add fee pool and destroy contract")
    @lcc.disabled()
    @lcc.tags("Bug: 'ECHO-1011'")
    @lcc.depends_on("DatabaseApi.GetContractFeePoolBalances.GetContractFeePoolBalances.method_main_check")
    def add_fee_pool_and_destroy_contract(self, get_random_integer_up_to_ten):
        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy, callee=contract_id)
        needed_fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id,
                                                        needed_fee + get_random_integer_up_to_ten,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Get balance of account and store")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' '{}' assets".format(self.echo_acc0, account_balance, self.echo_asset))

        lcc.set_step("Get a contract's fee pool balance before contract destroyed")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        fee_pool_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'. "
                     "Fee pool balance: '{}' assets".format(contract_id, fee_pool_balance))

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Check contract fee pool balance after contract destroyed")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        fee_pool_balance_after_destroy = self.get_response(response_id)["result"]["amount"]
        check_that("'contract pool balance'", fee_pool_balance_after_destroy, equal_to(0))

        lcc.set_step("Check account balance for refund")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        updated_account_balance = self.get_response(response_id)["result"][0]["amount"]
        check_that("'account balance'", updated_account_balance,
                   equal_to(account_balance + fee_pool_balance - needed_fee))

    @lcc.prop("type", "method")
    @lcc.test("Add insufficient fee pool to contract to call contract method")
    @lcc.depends_on("DatabaseApi.GetContractFeePoolBalances.GetContractFeePoolBalances.method_main_check")
    def add_insufficient_fee_pool_to_call_contract(self):
        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to perform the call contract 'greet' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        needed_fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        value_to_pool = self.get_random_amount(needed_fee)
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info(
            "Added '{}' assets value to '{}' contract fee pool successfully".format(value_to_pool, contract_id))

        lcc.set_step("Get balances of new account and store")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' '{}' assets".format(self.echo_acc0, account_balance, self.echo_asset))

        lcc.set_step("Get a contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        fee_pool_balance = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'. "
                     "Fee pool balance: '{}' assets".format(contract_id, fee_pool_balance))

        lcc.set_step("Call 'greet' method using new account, that don't have any balance")
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get a contract's fee pool balance after contract call")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        updated_fee_pool_balance = self.get_response(response_id)["result"]["amount"]

        lcc.set_step("Check that contract pool balance became empty")
        check_that("'contract pool balance'", updated_fee_pool_balance, equal_to(fee_pool_balance - value_to_pool))

        lcc.set_step("Get updated balances of new account and check it")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        updated_account_balance = self.get_response(response_id)["result"][0]["amount"]
        check_that("'account balance'", int(updated_account_balance),
                   equal_to(int(account_balance) - (needed_fee - value_to_pool)))


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("asset_api", "get_contract_fee_pool_balances")
@lcc.suite("Negative testing of method 'get_contract_fee_pool_balances'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Add to contract fee pool not echo asset")
    @lcc.depends_on("DatabaseApi.GetContractFeePoolBalances.GetContractFeePoolBalances.method_main_check")
    def add_fee_pool_in_not_echo_asset(self, get_random_valid_asset_name, get_random_integer,
                                       get_random_integer_up_to_ten):
        new_asset_name = get_random_valid_asset_name
        asset_value = get_random_integer
        value_to_pool = get_random_integer_up_to_ten

        lcc.set_step("Create a new asset and get id new asset")
        new_asset_id = self.utils.get_asset_id(self, new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset_id))

        lcc.set_step("Add new asset to account")
        self.utils.add_assets_to_account(self, asset_value, new_asset_id, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.log_info("'{}' account became new asset holder of '{}' asset_id".format(self.echo_acc0, new_asset_id))

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        try:
            self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                            self.__database_api_identifier, value_asset_id=new_asset_id)
            lcc.log_error("Error: broadcast transaction complete with not echo asset - '{}'.".format(new_asset_id))
        except RPCError as e:
            lcc.log_info(str(e))
