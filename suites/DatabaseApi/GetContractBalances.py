# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from lemoncheesecake.matching import this_dict, check_that_entry, equal_to

from common.base_test import BaseTest
import random

SUITE = {
    "description": "Method 'get_contract_balances'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_contract_balances")
@lcc.suite("Check work of method 'get_contract_balances'", rank=1)
class GetContractBalances(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
        echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                        self.__registration_api_identifier)
        lcc.set_step("Create contract in the Echo network and get its contract id")

        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=echo_acc0,
                                                                value_amount=value_amount, bytecode=self.contract)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]

        with this_dict(response):
            check_that_entry("amount", equal_to(value_amount))
            check_that_entry("asset_id", equal_to(self.echo_asset))


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_contract_balances")
@lcc.suite("Positive testing of method 'get_contract_balances'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.contract_getPennie = self.get_byte_code("piggy", "getPennie")
        self.storage_contract = self.get_byte_code("storage", "code")
        self.storage_setGreeting = self.get_byte_code("storage", "setGreeting")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @staticmethod
    def proliferate_asset_names(asset_name_base, total_asset_count):
        return ['{}{}'.format(asset_name_base, 'A' * num) for num in range(total_asset_count)]

    @staticmethod
    def proliferate_value_amount(total_rand_int_count):
        return [random.randrange(100, 1000) for num in range(total_rand_int_count)]

    @lcc.prop("type", "method")
    @lcc.test("Work of method 'get_contract_balances' with getPennie method and asset")
    @lcc.depends_on("DatabaseApi.GetContractBalances.GetContractBalances.method_main_check")
    def check_method_with_new_asset(self, get_random_integer, get_random_valid_asset_name):
        value_amount = get_random_integer

        asset_name = get_random_valid_asset_name
        lcc.set_step("Create asset and get new asset id")
        asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(asset_id))
        lcc.set_step("Add asset to account")
        self.utils.add_assets_to_account(self, value_amount, asset_id, self.echo_acc0,
                                         self.__database_api_identifier)

        lcc.set_step("Create contract with new asset id")
        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                value_amount=value_amount, bytecode=self.contract,
                                                                value_asset_id=asset_id, supported_asset_id=asset_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)

        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        with this_dict(response):
            check_that_entry("amount", equal_to(value_amount))
            check_that_entry("asset_id", equal_to(asset_id))

        lcc.set_step("Call 'getPennie' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.contract_getPennie, callee=contract_id,
                                                              value_asset_id=asset_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]

        with this_dict(response):
            check_that_entry("amount", equal_to(value_amount - 1))
            check_that_entry("asset_id", equal_to(asset_id))

    @lcc.prop("type", "method")
    @lcc.test("Work of contract method 'setGreeting' with 2 assets")
    @lcc.depends_on("DatabaseApi.GetContractBalances.GetContractBalances.method_main_check")
    def check_method_with_new_contract(self, get_random_string, get_random_valid_asset_name):
        lcc.set_step("Create contract")
        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.storage_contract,
                                                                supported_asset_id=None)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)

        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        lcc.set_step("Generate assets")
        asset_name_base = get_random_valid_asset_name
        total_proliferate_count = 2
        generated_assets = self.proliferate_asset_names(asset_name_base, total_proliferate_count)
        lcc.log_info('Generated asset names: {}'.format(generated_assets))

        list_operations = []
        random_string = get_random_string
        byte_code = self.get_byte_code_param(random_string, str)
        value_amount = self.proliferate_value_amount(total_proliferate_count)
        asset_ids = []

        lcc.set_step("Add assets to account")
        for i, asset_name in enumerate(generated_assets):
            asset_ids.append(self.utils.get_asset_id(self, asset_name, self.__database_api_identifier))
            operation = self.echo_ops.get_asset_issue_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                value_amount=value_amount[i],
                                                                value_asset_id=asset_ids[-1],
                                                                issue_to_account=self.echo_acc0)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            list_operations.append(collected_operation)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations,
                                                   log_broadcast=False)

        lcc.set_step("Call 'setGreeting' method")
        for i, asset_id in enumerate(asset_ids):
            operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=self.storage_setGreeting + byte_code,
                                                                  callee=contract_id, value_amount=value_amount[i],
                                                                  value_asset_id=asset_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            list_operations.append(collected_operation)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations,
                                                   log_broadcast=False)

        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]

        for i, result in enumerate(response):
            with this_dict(result):
                check_that_entry("amount", equal_to(value_amount[i]))
                check_that_entry("asset_id", equal_to(asset_ids[i]))
