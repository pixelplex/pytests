# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_balances'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract_balances")
@lcc.suite("Check work of method 'get_contract_balances'", rank=1)
class GetContractBalances(BaseTest):

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=value_amount)

        lcc.set_step("Get contract balances")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_contract_balances' with param: '{}'".format(contract_id))

        lcc.set_step("Check main fields")
        with this_dict(response):
            check_that_entry("amount", equal_to(value_amount))
            check_that_entry("asset_id", equal_to(self.echo_asset))


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_contract_balances")
@lcc.suite("Positive testing of method 'get_contract_balances'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")
        self.storage_contract = self.get_byte_code("storage", "code")
        self.storage_setGreeting = self.get_byte_code("storage", "setGreeting(string)")

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

    @staticmethod
    def proliferate_asset_names(asset_name_base, total_asset_count):
        return ['{}{}'.format(asset_name_base, 'A' * num) for num in range(total_asset_count)]

    @staticmethod
    def proliferate_value_amount(_to, total_rand_int_count, _from=1):
        return [random.randrange(_from, _to + num) for num in range(total_rand_int_count)]

    @lcc.prop("type", "method")
    @lcc.test("Get contract balance in new asset")
    @lcc.depends_on("DatabaseApi.GetContractBalances.GetContractBalances.method_main_check")
    def check_contract_balance_in_new_asset(self, get_random_integer, get_random_valid_asset_name):
        value_amount = get_random_integer
        asset_name = get_random_valid_asset_name

        lcc.set_step("Create asset and get new asset id")
        new_asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset_id))

        lcc.set_step("Add asset to account")
        self.utils.add_assets_to_account(self, value_amount, new_asset_id, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.log_info("'{}' account became new asset holder of '{}' asset_id".format(self.echo_acc0, new_asset_id))

        lcc.set_step(
            "Create contract in the Echo network and get it's contract id. Value and supported asset is new asset")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount,
                                                 value_asset_id=new_asset_id, supported_asset_id=new_asset_id)

        lcc.set_step("Get contract balances and check balance in new asset")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        with this_dict(result):
            check_that_entry("amount", equal_to(value_amount))
            check_that_entry("asset_id", equal_to(new_asset_id))

        lcc.set_step("Call 'getPennie' method to contract balance change check")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_pennie, callee=contract_id,
                                                              value_asset_id=new_asset_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get contract balances and check updated contract balance")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        with this_dict(result):
            check_that_entry("amount", equal_to(value_amount - 1))
            check_that_entry("asset_id", equal_to(new_asset_id))

    @lcc.prop("type", "method")
    @lcc.test("Get contract balance in several assets")
    @lcc.depends_on("DatabaseApi.GetContractBalances.GetContractBalances.method_main_check")
    def check_contract_with_balance_in_several_assets(self, get_random_valid_asset_name, get_random_integer_up_to_fifty,
                                                      get_random_string):
        count = 2
        new_asset_ids = []
        list_operations = []

        lcc.set_step("Create contract in the Echo network and get it's contract id. Supported asset is None")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.storage_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Create assets and add them to account")
        generated_asset_names = self.proliferate_asset_names(get_random_valid_asset_name, count)
        value_amounts = self.proliferate_value_amount(get_random_integer_up_to_fifty, count)
        for i, asset_name in enumerate(generated_asset_names):
            new_asset_ids.append(self.utils.get_asset_id(self, asset_name, self.__database_api_identifier))
            self.utils.add_assets_to_account(self, value_amounts[i], new_asset_ids[i], self.echo_acc0,
                                             self.__database_api_identifier)

        lcc.set_step("Call 'setGreeting' method to add several assets to contract balance")
        argument = self.get_byte_code_param(get_random_string, str)
        for i, asset_id in enumerate(new_asset_ids):
            operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=self.storage_setGreeting + argument,
                                                                  callee=contract_id, value_amount=value_amounts[i],
                                                                  value_asset_id=asset_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            list_operations.append(collected_operation)
        self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations)

        lcc.set_step("Get contract balances and check contract balance in several asset")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        for i, result in enumerate(response["result"]):
            with this_dict(result):
                check_that_entry("amount", equal_to(value_amounts[i]))
                check_that_entry("asset_id", equal_to(new_asset_ids[i]))
