# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'call_contract_no_changing_state'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "call_contract_no_changing_state")
@lcc.suite("Check work of method 'call_contract_no_changing_state'", rank=1)
class CallContractNoChangingState(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")

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
    @lcc.test("Simple work of method 'call_contract_no_changing_state'")
    def method_main_check(self):
        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Get call contract operation no changing state")
        params = [contract_id, self.echo_acc0, self.echo_asset, self.greet]
        response_id = self.send_request(self.get_request("call_contract_no_changing_state", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'call_contract_no_changing_state' with params: '{}'".format(params))

        lcc.set_step("Check simple work of method 'call_contract_no_changing_state'")
        if not self.validator.is_hex(result):
            lcc.log_error("Wrong format of response from 'call_contract_no_changing_state', got: {}".format(result))
        else:
            lcc.log_info("response from 'call_contract_no_changing_state' has correct format: hex")


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "call_contract_no_changing_state")
@lcc.suite("Positive testing of method 'call_contract_no_changing_state'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")
        self.getPennie = self.get_byte_code("piggy", "getPennie")
        self.contract_dynamic_fields = self.get_byte_code("dynamic_fields", "code")
        self.set_uint = self.get_byte_code("dynamic_fields", "onUint256Changed(uint256)")
        self.get_uint = self.get_byte_code("dynamic_fields", "getUint256()")

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
    @lcc.test("Check work of 'call_contract_no_changing_state' method, not empty call contract result")
    @lcc.depends_on("DatabaseApi.CallContractNoChangingState.CallContractNoChangingState.method_main_check")
    def check_call_contract_no_changing_state_with_not_empty_call_contract_result(self):
        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Call method of piggy contract: 'greet'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Method 'greet' performed successfully")

        lcc.set_step("Get contract result output")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output_in_hex = self.get_contract_output(contract_result, in_hex=True)

        lcc.set_step("Get call contract operation no changing state")
        params = [contract_id, self.echo_acc0, self.echo_asset, self.greet]
        response_id = self.send_request(self.get_request("call_contract_no_changing_state", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'call_contract_no_changing_state' with params: '{}'".format(params))

        lcc.set_step("Check call contract operation no changing state equal to call contract result")
        check_that("'call contract operation no changing state'", result, equal_to(contract_output_in_hex), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test(
        "Check work of 'call_contract_no_changing_state' method, empty call contract result but with new asset_id")
    @lcc.tags("qa")
    # @lcc.depends_on("DatabaseApi.CallContractNoChangingState.CallContractNoChangingState.method_main_check")
    def check_call_contract_no_changing_state_with_empty_call_contract_result(self, get_random_valid_asset_name,
                                                                              get_random_integer):
        value_amount = get_random_integer
        asset_name = get_random_valid_asset_name

        lcc.set_step("Create asset and get id new asset")
        new_asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset_id))

        lcc.set_step("Add created asset to account")
        self.utils.add_assets_to_account(self, value_amount, new_asset_id, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.log_info("'{}' account became new asset holder of '{}' asset_id".format(self.echo_acc0, new_asset_id))

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_asset_id=new_asset_id,
                                                 value_amount=value_amount, supported_asset_id=new_asset_id)

        lcc.set_step("Call method of piggy contract: 'getPennie'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id,
                                                              value_asset_id=new_asset_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get contract result output")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output_in_hex = self.get_contract_output(contract_result, in_hex=True)

        lcc.set_step("Get call contract operation no changing state")
        params = [contract_id, self.echo_acc0, new_asset_id, self.getPennie]
        response_id = self.send_request(self.get_request("call_contract_no_changing_state", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'call_contract_no_changing_state' with params: '{}'".format(params))

        lcc.set_step("Check call contract operation no changing state equal to call contract result")
        check_that("'call contract operation no changing state'", result, equal_to(contract_output_in_hex), quiet=True)

    # todo stop here

    @lcc.prop("type", "method")
    @lcc.test("Check contract output with int value using 'call_contract_no_changing_state'")
    @lcc.depends_on("DatabaseApi.CallContractNoChangingState.CallContractNoChangingState.method_main_check")
    def check_contract_with_two_output(self, get_random_integer):
        int_param = get_random_integer

        lcc.set_step("Create 'dynamic_fields' contract in ECHO network")
        contract_dynamic_fields_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_dynamic_fields,
                                                                self.__database_api_identifier)

        lcc.set_step("Get contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_dynamic_fields_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with param: '{}'".format(contract_dynamic_fields_id))

        lcc.set_step("Check storage of created contract without any fields")
        contract_storage = response["result"][1]["storage"]
        check_that("'contract storage'", contract_storage, is_list([]), quiet=True)

        lcc.set_step("Call method 'set_uint' to add uint field in contract")
        bytecode = self.set_uint + self.get_byte_code_param(int_param, param_type=int)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

        lcc.set_step("Call method 'get_uint'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_uint,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = contract_result["result"][1]["exec_res"]["output"]
        contract_output_value = self.get_contract_output(contract_result, output_type=int)

        lcc.set_step("Get response of 'call_contract_no_changing_state'")
        response_id = self.send_request(self.get_request("call_contract_no_changing_state",
                                                         [contract_dynamic_fields_id, self.echo_acc0, self.echo_asset,
                                                          self.get_uint]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("{}".format(result))
        lcc.set_step(
            "Check value of contract result and that result output equal to 'call_contract_no_changing_state' result")
        check_that("'uint field in contract'", contract_output_value, equal_to(int_param))
        check_that("contract_output", result, equal_to(contract_output))
