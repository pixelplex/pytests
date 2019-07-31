# -*- coding: utf-8 -*-
import re

import lemoncheesecake.api as lcc
from echopy import Echo
from lemoncheesecake.matching import this_dict, equal_to, check_that_entry, is_integer, is_list, is_dict, is_str, \
    ends_with, check_that, require_that, greater_than, has_length, require_that_entry, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_result'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract_result")
@lcc.suite("Check work of method 'get_contract_result'", rank=1)
class GetContractResult(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

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

    @staticmethod
    def check_zero_bloom(bloom):
        check_zero_bloom = re.compile(r"(0*)$")
        if bool(check_zero_bloom.match(bloom)):
            lcc.log_info("'bloom' has correct format '000...0'")
        else:
            lcc.log_error("Wrong format of 'bloom', got: {}".format(bloom))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_result'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Create 'piggy' contract")
        contract = self.utils.get_contract_id(self, self.echo_acc0, self.piggy, self.__database_api_identifier,
                                              value_amount=value_amount, need_broadcast_result=True)
        contract_result_id = self.get_operation_results_ids(contract.get("broadcast_result"))

        lcc.set_step("Get contract result of created contract")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        contract_result = response["result"][1]
        lcc.log_info(
            "Call method 'get_contract_result' with contract_result_id='{}' parameter".format(contract_result_id))

        lcc.set_step("Check contract create result")
        with this_dict(contract_result):
            if check_that("contract_result", contract_result, has_length(2)):
                check_that_entry("exec_res", is_dict(), quiet=True)
                check_that_entry("tr_receipt", is_dict(), quiet=True)
                exec_res = contract_result["exec_res"]
                with this_dict(exec_res):
                    if check_that("exec_res", exec_res, has_length(7)):
                        require_that_entry("excepted", equal_to("None"), quiet=True)
                        if not self.validator.is_hex(exec_res["new_address"]):
                            lcc.log_error("Wrong format of 'new_address', got: {}".format(exec_res["new_address"]))
                        else:
                            lcc.log_info("'new_address' has correct format: hex")
                        contract_id = self.get_contract_id(response)
                        contract_output_in_hex = exec_res["output"]
                        if not self.validator.is_hex(contract_output_in_hex):
                            lcc.log_error("Wrong format of 'output', got: {}".format(contract_output_in_hex))
                        else:
                            lcc.log_info("'output' has correct format: hex")
                        require_that_entry("code_deposit", equal_to("Success"), quiet=True)
                        # todo: 'gas_refunded' will removed. Improvement ECHO-1015
                        check_that_entry("gas_refunded", is_integer(), quiet=True)
                        check_that_entry("gas_for_deposit", greater_than(0), quiet=True)
                        contract_output_bytecode_length = len(contract_output_in_hex)
                        check_that_entry("deposit_size", equal_to(contract_output_bytecode_length // 2), quiet=True)
                tr_receipt = contract_result["tr_receipt"]
                with this_dict(tr_receipt):
                    if check_that("tr_receipt", tr_receipt, has_length(4)):
                        check_that_entry("status_code", equal_to(1), quiet=True)
                        # Note: the value in the field 'gas_used' is checked in the 'GasUsed' scenario
                        check_that_entry("gas_used", greater_than(0), quiet=True)
                        require_that_entry("log", equal_to([]), quiet=True)
                        self.check_zero_bloom(tr_receipt["bloom"])

        lcc.set_step("Call method 'getPennie'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie,
                                                              callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_call_result_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info(
            "Method 'getPennie' performed successfully, contract call result id: '{}'".format(contract_call_result_id))

        lcc.set_step("Get contract call result of created contract")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_call_result_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        contract_call_result = response["result"][1]
        lcc.log_info(
            "Call method 'get_contract_result' with contract_call_result_id='{}' parameter".format(contract_result_id))

        lcc.set_step("Check contract call result")
        with this_dict(contract_call_result):
            if check_that("contract_call_result", contract_call_result, has_length(2)):
                exec_res = contract_call_result["exec_res"]
                with this_dict(exec_res):
                    if check_that("exec_res", exec_res, has_length(7)):
                        require_that_entry("excepted", equal_to("None"), quiet=True)
                        check_that_entry("output", is_str(), quiet=True)
                        require_that_entry("code_deposit", equal_to("None"), quiet=True)
                        # todo: 'gas_refunded' will removed. Improvement ECHO-1015
                        require_that_entry("gas_refunded", equal_to(0), quiet=True)
                        require_that_entry("gas_for_deposit", equal_to(0), quiet=True)
                        require_that_entry("deposit_size", equal_to(0), quiet=True)
                tr_receipt = contract_call_result["tr_receipt"]
                with this_dict(tr_receipt):
                    if check_that("tr_receipt", tr_receipt, has_length(4)):
                        check_that_entry("status_code", equal_to(1), quiet=True)
                        # Note: the value in the field 'gas_used' is checked in the 'GasUsed' scenario
                        check_that_entry("gas_used", greater_than(0), quiet=True)
                        logs = tr_receipt["log"]
                        check_that_entry("log", is_list(), quiet=True)
                        require_that("'log has value'", bool(logs), is_true(), quiet=True)
                        for log in logs:
                            with this_dict(log):
                                contract_id_that_called = self.get_contract_id(response, contract_call_result=True)
                                require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
                                log_values = log["log"]
                                for log_value in log_values:
                                    if not self.validator.is_hex(log_value):
                                        lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                                    else:
                                        lcc.log_info("'log_value' has correct format: hex")
                                check_that_entry("data", is_str())
                        if not self.validator.is_hex(tr_receipt["bloom"]):
                            lcc.log_error("Wrong format of 'bloom', got: {}".format(tr_receipt["bloom"]))
                        else:
                            lcc.log_info("'bloom' has correct format: hex")


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_contract_result")
@lcc.suite("Positive testing of method 'get_contract_result'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

        self.setAllValues_method_name = "setAllValues(uint256,string)"
        self.setString_method_name = "onStringChanged(string)"
        self.setUint256_method_name = "onUint256Changed(uint256)"
        self.contract_dynamic_fields = self.get_byte_code("dynamic_fields", "code")
        self.set_all_values = self.get_byte_code("dynamic_fields", self.setAllValues_method_name)
        self.echo = Echo()

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

    @staticmethod
    def get_contract_from_address(self, contract_identifier_hex):
        contract_id = "{}{}".format("{}.{}.".format(
            self.echo.config.reserved_spaces.PROTOCOL_IDS,
            self.echo.config.object_types.CONTRACT),
            int(str(contract_identifier_hex)[2:], 16))
        if not self.validator.is_contract_id(contract_id):
            lcc.log_error("Wrong format of contract id, got {}".format(contract_id))
        return contract_id

    @lcc.prop("type", "method")
    @lcc.test("Check contract info using method 'greet'")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_info_after_calling_greet_contract_method(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call method of piggy contract: 'greet'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)

        lcc.set_step("Get contract output")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        expected_string = "Hello World!!!"
        contract_output = self.get_contract_output(contract_result, output_type=str,
                                                   len_output_string=len(expected_string))

        lcc.set_step("Check 'greet' method result")
        check_that("output", contract_output, equal_to(expected_string))

    @lcc.prop("type", "method")
    @lcc.test("Check create contract info of 'piggy' contract")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_info_after_create_contract(self, get_random_valid_asset_name, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Сreate piggy contract, and get contract_id and contract result")
        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract_piggy,
                                                                value_amount=value_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        operation_results_ids = self.get_operation_results_ids(broadcast_result)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        response_id = self.send_request(self.get_request("get_contract_result", [operation_results_ids]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][1]
        lcc.set_step("Get contract code form 'get_contract' method")
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        contract_code = self.get_response(response_id)["result"][1]["code"]

        lcc.set_step("Check create contract output")
        with this_dict(result):
            check_that("output", self.contract_piggy, ends_with(result["exec_res"]["output"]), quiet=True)
            check_that("output", result["exec_res"]["output"], equal_to(contract_code), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs of two different contracts")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_info_of_two_different_contract_logs(self, get_random_integer, get_random_string):
        int_param = get_random_integer
        string_param = get_random_string

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_dynamic_fields_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_dynamic_fields,
                                                                self.__database_api_identifier)

        lcc.set_step("Call method 'set_all_values' with int: {} and string: {} params".format(int_param, string_param))
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        bytecode = self.set_all_values + int_param_code + string_param_code
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)

        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        operation_results_id = self.get_operation_results_ids(broadcast_result)
        lcc.set_step("Get contract result")
        response_id = self.send_request(self.get_request("get_contract_result", [operation_results_id]),
                                        self.__database_api_identifier)

        result = self.get_response(response_id, log_response=True)["result"][1]["tr_receipt"]["log"]
        lcc.set_step("Check contract logs")
        call_contact_log0 = result[0]
        call_contract_log1 = result[1]
        contract_id_from_address = self.get_contract_from_address(self, call_contact_log0["address"])

        check_that("contract_id", contract_dynamic_fields_id, equal_to(contract_id_from_address))
        check_that("address", call_contact_log0["address"], equal_to(call_contract_log1["address"]))

        check_that("log of 'set_uint' method", call_contact_log0["log"], is_list(), quiet=True)
        check_that("log of 'set_string' method", call_contract_log1["log"], is_list(), quiet=True)

        keccak_log0 = self.keccak_log_value(self.setUint256_method_name, log_info=True)
        keccak_log1 = self.keccak_log_value(self.setString_method_name, log_info=True)
        check_that("log value", call_contact_log0["log"][0], equal_to(keccak_log0))
        check_that("log value1", call_contract_log1["log"][0], equal_to(keccak_log1))

        data0 = self.get_contract_log_data(call_contact_log0, output_type=int)
        data1 = self.get_contract_log_data(call_contract_log1, output_type=str)
        check_that("data", data0, equal_to(int_param))
        check_that("data", data1, equal_to(string_param))

# todo: add bloom test
