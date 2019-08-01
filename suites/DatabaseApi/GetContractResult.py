# -*- coding: utf-8 -*-
import re

import lemoncheesecake.api as lcc
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
        lcc.log_info("Call method 'get_contract_result' with contract_result_id='{}' param".format(contract_result_id))

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
            "Call method 'get_contract_result' with contract_call_result_id='{}' param".format(contract_result_id))

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
                                contract_id_that_called = self.get_contract_id(response, contract_call_result=True,
                                                                               new_contract=False)
                                require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
                                log_values = log["log"]
                                for log_value in log_values:
                                    if not self.validator.is_hex(log_value):
                                        lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                                    else:
                                        lcc.log_info("'log_value' has correct format: hex")
                                check_that_entry("data", is_str(), quiet=True)
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
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.setString_method_name = "onStringChanged(string)"
        self.setUint256_method_name = "onUint256Changed(uint256)"
        self.set_all_values = self.get_byte_code("dynamic_fields", "setAllValues(uint256,string)")

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
    @lcc.test("Get contract result using method that return string value")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_result_that_return_string_value(self):
        expected_string = "Hello World!!!"

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Call method of piggy contract: 'greet'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_call_result_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info(
            "Method 'greet' performed successfully, contract call result id: '{}'".format(contract_call_result_id))

        lcc.set_step("Get contract call result of created contract")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_call_result_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'get_contract_result' with contract_call_result_id='{}' param".format(contract_call_result_id))

        lcc.set_step("Get output from the execution of the contract method and check returned value")
        contract_output = self.get_contract_output(response, output_type=str, len_output_string=len(expected_string))
        check_that("output", contract_output, equal_to(expected_string))

    @lcc.prop("type", "method")
    @lcc.test("Check output from the execution of the 'piggy' contract creation")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_result_of_contract_creation(self):
        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract, self.__database_api_identifier,
                                              need_broadcast_result=True)
        contract_result_id = self.get_operation_results_ids(contract.get("broadcast_result"))

        lcc.set_step("Get contract creation result and store")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result_id]),
                                        self.__database_api_identifier)
        contract_result_output = self.get_response(response_id)["result"][1]["exec_res"]["output"]
        lcc.log_info("Call method 'get_contract_result' with contract_result_id='{}' param".format(contract_result_id))

        lcc.set_step("Get contract code form 'get_contract' method and store")
        response_id = self.send_request(self.get_request("get_contract", [contract.get("contract_id")]),
                                        self.__database_api_identifier)
        contract_code = self.get_response(response_id)["result"][1]["code"]
        lcc.log_info("Call method 'get_contract' with '{}' created contract".format(contract.get("contract_id")))

        lcc.set_step("Compare contracts outputs between 'get_contract_result' and 'get_contract' methods")
        check_that("'contract result output'", self.piggy_contract, ends_with(contract_result_output), quiet=True)
        check_that("'contract result output'", contract_result_output, equal_to(contract_code), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract result of contract call that make two logs")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_result_of_contract_call_that_make_two_logs(self, get_random_integer, get_random_string):
        int_param = get_random_integer
        string_param = get_random_string

        lcc.set_step("Create 'dynamic_fields' contract in the Echo network and get it's contract id")
        dynamic_fields_contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.dynamic_fields_contract,
                                                                self.__database_api_identifier)

        lcc.set_step("Call method of dynamic_fields contract: 'set_all_values'")
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        method_params = int_param_code + string_param_code
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.set_all_values + method_params,
                                                              callee=dynamic_fields_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_call_result_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Method 'set_all_values' performed successfully, contract call result id: '{}'"
                     "".format(contract_call_result_id))

        lcc.set_step("Get contract call result of created contract")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_call_result_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        dynamic_fields_contract_call_logs = response["result"][1]["tr_receipt"]["log"]
        lcc.log_info(
            "Call method 'get_contract_result' with contract_call_result_id='{}' param".format(contract_call_result_id))

        lcc.set_step("Check contract result with several logs")
        for i, log in enumerate(dynamic_fields_contract_call_logs):
            lcc.log_info("Check log#'{}'".format(i))
            with this_dict(log):
                contract_id_that_called = self.get_contract_id(response, contract_call_result=True, new_contract=False)
                require_that("contract_id", contract_id_that_called, equal_to(dynamic_fields_contract_id), quiet=True)
                log_values = log["log"]
                for log_value in log_values:
                    if not self.validator.is_hex(log_value):
                        lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                    else:
                        lcc.log_info("'log_value' has correct format: hex")
                if not self.validator.is_hex(log["data"]):
                    lcc.log_error("Wrong format of 'data', got: {}".format(log["data"]))
                else:
                    lcc.log_info("'data' has correct format: hex")
        for i in range(len(dynamic_fields_contract_call_logs))[:-1]:
            check_that(
                "'addresses in contract call result are the same'",
                dynamic_fields_contract_call_logs[i]["address"] == dynamic_fields_contract_call_logs[i + 1]["address"],
                is_true()
            )

        lcc.set_step("Check contract result log value")
        method_names_in_keccak_std = [self.get_keccak_standard_value(self.setUint256_method_name),
                                      self.get_keccak_standard_value(self.setString_method_name)]
        for i, log in enumerate(dynamic_fields_contract_call_logs):
            check_that("'log value'", log["log"][0], equal_to(method_names_in_keccak_std[i]), quiet=True)

        lcc.set_step("Check contract result log data")
        call_contract_params = [int_param, string_param]
        output_types = [int, str]
        log_data = self.get_contract_log_data(response, output_type=output_types)
        for i, data in enumerate(log_data):
            lcc.log_info("Check data#'{}'".format(i))
            check_that("'converted 'data' from hex'", data, equal_to(call_contract_params[i]))

# todo: add test for testing bloom field
