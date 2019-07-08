# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, equal_to, check_that_entry, is_integer, is_list,\
    is_dict, is_str, ends_with, check_that, require_that, greater_than, has_item, is_none

from common.base_test import BaseTest
import re
import random
from echopy import Echo

SUITE = {
    "description": "Method 'get_contract_result'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_contract_result")
@lcc.suite("Check work of method 'get_contract_result'", rank=1)
class GetContractResult(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.piggy = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "getPennie")

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
    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @staticmethod
    def check_zero_bloom(bloom):
        check_zero_bloom = re.compile(r"(0*)$")
        if bool(check_zero_bloom.match(bloom)):
            lcc.log_info("'bloom' has correct format '000...0'")
        else:
            lcc.log_error("Wrong format of 'bloom' some of values is not '0'")

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_result'")
    def method_main_check(self, get_random_valid_asset_name, get_random_integer):
        value_amount = get_random_integer
        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                value_amount=value_amount,
                                                                bytecode=self.piggy)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        contract_result_id = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)
        result_contract_id = self.get_contract_id(result)
        check_that("contract_id", contract_id, equal_to(result_contract_id))
        result = result["result"][1]
        with this_dict(result):
            check_that_entry("exec_res", is_dict(), quiet=True)
            check_that_entry("tr_receipt", is_dict(), quiet=True)
            with this_dict(result["exec_res"]):
                if require_that("excepted", result["exec_res"]["excepted"], equal_to("None")):
                    if not self.validator.is_hex(result["exec_res"]["new_address"]):
                        lcc.log_error("Wrong format of 'new_address', got: {}".format(result["exec_res"]["new_address"]))
                    else:
                        lcc.log_info("'new_address' has correct format: hex")
                        contract_output_in_hex = result["exec_res"]["output"]
                    if not self.validator.is_hex(contract_output_in_hex):
                        lcc.log_error("Wrong format of 'output', got: {}".format(contract_output_in_hex))
                    else:
                        lcc.log_info("'output' has correct format: hex")
                    if require_that("code_deposit", result["exec_res"]["code_deposit"], equal_to("Success")):
                        # todo: will removed. Improvement ECHO-1015
                        check_that_entry("gas_refunded", is_integer())
                        check_that_entry("gas_for_deposit", greater_than(0))
                        len_bytecode_of_contract_output = len(contract_output_in_hex) // 2
                        check_that_entry("deposit_size", equal_to(len_bytecode_of_contract_output))
        with this_dict(result["tr_receipt"]):
            check_that_entry("status_code", equal_to(1))
            # Note: check in 'GasUsed' scenario
            check_that_entry("gas_used", greater_than(0))
            if require_that("log", result["tr_receipt"]["log"], equal_to([])):
                self.check_zero_bloom(result["tr_receipt"]["bloom"])
                if not self.validator.is_hex(result["tr_receipt"]["bloom"]):
                        lcc.log_error("Wrong format of 'bloom', got: {}".format(result["tr_receipt"]["bloom"]))
                else:
                    lcc.log_info("'bloom' has correct format: hex")
            check_that_entry("log", is_list())
        lcc.set_step("call operation")

        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result_id = self.get_operation_results_ids(broadcast_result)

        response_id = self.send_request(self.get_request("get_contract_result", [contract_result_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][1]
        with this_dict(result):
            check_that_entry("exec_res", is_dict(), quiet=True)
            check_that_entry("tr_receipt", is_dict(), quiet=True)
            with this_dict(result["exec_res"]):
                if require_that("excepted", result["exec_res"]["excepted"], equal_to("None")):
                    check_that_entry("output", is_str())
                    check_that_entry("code_deposit", is_str())
                    # todo: will removed. Improvement ECHO-1015
                    check_that_entry("gas_refunded", is_integer())
                    check_that_entry("gas_for_deposit", equal_to(0))
                    check_that_entry("deposit_size", equal_to(0))
        with this_dict(result["tr_receipt"]):
            check_that_entry("status_code", is_integer())
            # Note: check in 'GasUsed' scenario
            check_that_entry("gas_used", is_integer())
            if not self.validator.is_hex(result["tr_receipt"]["bloom"]):
                    lcc.log_error("Wrong format of 'bloom', got: {}".format(result["tr_receipt"]["bloom"]))
            else:
                lcc.log_info("'bloom' has correct format: hex")
            check_that_entry("log", is_list(), quiet=True)
            with this_dict(result["tr_receipt"]["log"][0]):
                log_valuse = result["tr_receipt"]["log"][0]
                if not self.validator.is_hex(log_valuse["address"]):
                    lcc.log_error("Wrong format of 'address', got: {}".format(log_valuse["address"]))
                else:
                    lcc.log_info("'address' has correct format: hex")
                check_that_entry("log", is_list(), quiet=True)
                if not self.validator.is_hex(log_valuse["log"][0]):
                    lcc.log_error("Wrong format of 'address', got: {}".format(log_valuse["log"][0]))
                else:
                    lcc.log_info("'address' has correct format: hex")
                check_that_entry("data", is_str())


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_contract_result")
@lcc.suite("Positive testing of method 'get_contract_result'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")
        self.getPennie = self.get_byte_code("piggy", "getPennie")
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
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @staticmethod
    def check_zero_bloom(bloom):
        check_zero_bloom = re.compile(r"(0*)$")
        if bool(check_zero_bloom.match(bloom)):
            lcc.log_info("'bloom' has correct format '000...0'")
        else:
            lcc.log_info("some of 'bloom' values is not '0'")

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
    @lcc.test("Get contract balance in several assets")
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
        operation_results_ids = self.get_operation_results_ids(broadcast_result)
        lcc.set_step("Get contract output")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        expected_string = "Hello World!!!"
        contract_output = self.get_contract_output(contract_result, output_type=str,
                                                   len_output_string=len(expected_string))
        response_id = self.send_request(self.get_request("get_contract_result", [operation_results_ids]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][1]

        check_that("output", contract_output, equal_to(expected_string))
        with this_dict(result):
            check_that_entry("exec_res", is_dict(), quiet=True)
            check_that_entry("tr_receipt", is_dict(), quiet=True)
            with this_dict(result["exec_res"]):
                check_that_entry("output", is_str(), quiet=True)
                check_that_entry("code_deposit", is_str())
                check_that_entry("gas_refunded", is_integer())
                check_that_entry("gas_for_deposit", equal_to(0))
                check_that_entry("deposit_size", equal_to(0))
        with this_dict(result["tr_receipt"]):
            check_that_entry("status_code", equal_to(1))
            check_that_entry("gas_used", greater_than(0))
            if not self.validator.is_hex(result["tr_receipt"]["bloom"]):
                    lcc.log_error("Wrong format of 'bloom', got: {}".format(result["tr_receipt"]["bloom"]))
            else:
                lcc.log_info("'bloom' has correct format: hex")
            check_that_entry("log", is_list())

    @lcc.prop("type", "method")
    @lcc.test("Check contract info using method 'getPennie'")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_info_after_calling_getPennie_contract_method(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)
        lcc.set_step("Call method of piggy contract: 'getPennie'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][1]
        with this_dict(result):
            check_that_entry("exec_res", is_dict(), quiet=True)
            check_that_entry("tr_receipt", is_dict(), quiet=True)
            with this_dict(result["exec_res"]):
                check_that_entry("output", is_str())
                check_that_entry("code_deposit", is_str())
                check_that_entry("gas_refunded", is_integer())
                check_that_entry("gas_for_deposit", equal_to(0))
                check_that_entry("deposit_size", equal_to(0))
        with this_dict(result["tr_receipt"]):
            check_that_entry("status_code", is_integer())
            check_that_entry("gas_used", is_integer())
            if not self.validator.is_hex(result["tr_receipt"]["bloom"]):
                    lcc.log_error("Wrong format of 'bloom', got: {}".format(result["tr_receipt"]["bloom"]))
            else:
                lcc.log_info("'bloom' has correct format: hex")
            check_that_entry("log", is_list(), quiet=True)
            with this_dict(result["tr_receipt"]["log"][0]):
                log_valuse = result["tr_receipt"]["log"][0]
                if not self.validator.is_hex(log_valuse["address"]):
                    lcc.log_error("Wrong format of 'address', got: {}".format(log_valuse["address"]))
                else:
                    lcc.log_info("'address' has correct format: hex")
                contract_id_from_address = self.get_contract_from_address(self, log_valuse["address"])
                check_that("contract_id", contract_id, equal_to(contract_id_from_address))
                check_that_entry("log", is_list(), quiet=True)
                if not self.validator.is_hex(log_valuse["log"][0]):
                    lcc.log_error("Wrong format of 'address', got: {}".format(log_valuse["log"][0]))
                else:
                    lcc.log_info("'address' has correct format: hex")
                check_that_entry("data", is_str())

    @lcc.prop("type", "method")
    @lcc.test("Check contract info using method 'greet'")
    @lcc.depends_on("DatabaseApi.GetContractResult.GetContractResult.method_main_check")
    def check_contract_info_after_create_contract(self, get_random_valid_asset_name, get_random_integer):
        asset_name = get_random_valid_asset_name
        value_amount = get_random_integer

        lcc.set_step("Create asset and get id new asset")
        asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(asset_id))
        lcc.set_step("Add asset to account")
        self.utils.add_assets_to_account(self, value_amount, asset_id, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.set_step("Сreate piggy contract")
        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract_piggy,
                                                                value_amount=value_amount, value_asset_id=asset_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        operation_results_ids = self.get_operation_results_ids(broadcast_result)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        response_id = self.send_request(self.get_request("get_contract_result", [operation_results_ids]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][1]
        with this_dict(result):
            check_that_entry("exec_res", is_dict(), quiet=True)
            check_that_entry("tr_receipt", is_dict(), quiet=True)
            with this_dict(result["exec_res"]):
                check_that_entry("excepted", equal_to("None"))
                if not self.validator.is_hex(result["exec_res"]["new_address"]):
                    lcc.log_error("Wrong format of 'new_address', got: {}".format(result["exec_res"]["new_address"]))
                else:
                    lcc.log_info("'new_address' has correct format: hex")
                contract_id_from_address = self.get_contract_from_address(self, result["exec_res"]["new_address"])
                check_that("contract_id", contract_id, equal_to(contract_id_from_address))
                check_that("output", self.contract_piggy, ends_with(result["exec_res"]["output"]), quiet=True)
                if require_that("code_deposit", result["exec_res"]["code_deposit"], equal_to("Success")):
                    # todo: will removed. Improvement ECHO-1015
                    check_that_entry("gas_refunded", is_integer())
                    check_that_entry("gas_for_deposit", greater_than(0))
                    check_that_entry("deposit_size", equal_to(len(result["exec_res"]["output"]) / 2))
        with this_dict(result["tr_receipt"]):
            if require_that("status_code", result["tr_receipt"]["status_code"], equal_to(1)):
                check_that_entry("gas_used", greater_than(0))
            if require_that("log", result["tr_receipt"]["log"], equal_to([])):
                self.check_zero_bloom(result["tr_receipt"]["bloom"])
                if not self.validator.is_hex(result["tr_receipt"]["bloom"]):
                        lcc.log_error("Wrong format of 'bloom', got: {}".format(result["tr_receipt"]["bloom"]))
                else:
                    lcc.log_info("'bloom' has correct format: hex")
