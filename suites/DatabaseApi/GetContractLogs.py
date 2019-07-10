# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, equal_to, is_list, is_str, check_that, \
    not_equal_to

import random

from common.base_test import BaseTest
from echopy import Echo
SUITE = {
    "description": "Method 'get_contract_logs'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_contract_logs")
@lcc.suite("Check work of method 'get_contract_logs'", rank=1)
class GetContractLogs(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
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
    @lcc.test("Simple work of method 'get_contract_logs'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier,
                                                 value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.set_step("Get contract logs from 0 block to current_block '{}'".format(block_num))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, block_num]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        with this_dict(result):
            check_that("lenght response", len(result), equal_to(3))
            contract_id_from_address = self.get_contract_from_address(self, result["address"])
            check_that("contract_id", contract_id, equal_to(contract_id_from_address))
            check_that_entry("log", is_list(), quiet=True)
            if not self.validator.is_hex(result["log"][0]):
                lcc.log_error("Wrong format of 'address', got: {}".format(result["log"][0]))
            else:
                lcc.log_info("'address' has correct format: hex")
            check_that_entry("data", is_str())


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_contract_logs")
@lcc.suite("Positive testing of method 'get_contract_logs'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "getPennie")
        self.contract_dynamic_fields = self.get_byte_code("dynamic_fields_with_logs", "code")
        self.set_uint = self.get_byte_code("dynamic_fields_with_logs", "setUint256")
        self.get_uint = self.get_byte_code("dynamic_fields_with_logs", "getUint256")
        self.delete_uint = self.get_byte_code("dynamic_fields_with_logs", "deleteUint256")
        self.set_string = self.get_byte_code("dynamic_fields_with_logs", "setString")
        self.get_string = self.get_byte_code("dynamic_fields_with_logs", "getString")
        self.delete_string = self.get_byte_code("dynamic_fields_with_logs", "deleteString")
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
    def get_contract_from_address(self, contract_identifier_hex):
        contract_id = "{}{}".format("{}.{}.".format(
            self.echo.config.reserved_spaces.PROTOCOL_IDS,
            self.echo.config.object_types.CONTRACT),
            int(str(contract_identifier_hex)[2:], 16))
        if not self.validator.is_contract_id(contract_id):
            lcc.log_error("Wrong format of contract id, got {}".format(contract_id))
        return contract_id

    @staticmethod
    def get_random_value(self, start, end):
        return random.randint(start, end)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs of two identical contracts")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_of_two_identical_contracts(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.set_step("Get contract logs from 0 block to current_block '{}'".format(block_num))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, block_num]),
                                        self.__database_api_identifier)
        result1 = self.get_response(response_id)["result"][0]
        lcc.set_step("Recall contract to have two identical logs")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.set_step("Get contract logs from 0 block to current_block '{}'".format(block_num))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, block_num]),
                                        self.__database_api_identifier)
        result2 = self.get_response(response_id)["result"][0]

        check_that("responses", result1, equal_to(result2))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs of two different contracts")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_of_two_different_contracts(self, get_random_integer, get_random_string):
        int_param = get_random_integer
        string_param = get_random_string
        contract_dynamic_fields_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_dynamic_fields,
                                                                self.__database_api_identifier)
        bytecode = self.set_uint + self.get_byte_code_param(int_param, param_type=int)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

        lcc.set_step("Check that uint field created in contract. Call method 'get_uint'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_uint,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        bytecode = self.set_string + self.get_byte_code_param(string_param, param_type=str)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

        lcc.set_step("Check that string field created in contract. Call method 'get_string'")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_string,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.set_step("Get contract logs from 0 block to current_block '{}'".format(block_num))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_dynamic_fields_id, 0, block_num]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]

        check_that("responses", result[0], not_equal_to(result[1]))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'start' to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_start_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.set_step("Pending the passage of several contracts")
        self.set_timeout_wait(10)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]
        lcc.set_step("Get contract logs from 0 block to head_block '{}'".format(head_block_number))

        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, head_block_number]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]

        with this_dict(result):
            check_that("lenght response", len(result), equal_to(3))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'start' to 'current_block'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_start_to_current_block(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.set_step("Get contract logs from 0 block to current_block '{}'".format(block_num))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, block_num]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        with this_dict(result):
            check_that("lenght response", len(result), equal_to(3))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'current_block' to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_current_block_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.log_info("get current_block number: {}".format(block_num))
        lcc.set_step("Pending the passage of several contracts")
        self.set_timeout_wait(10)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]
        lcc.set_step("Get contract logs from block with contract '{}'-1, to head block '{}'".format(block_num,
                                                                                                    head_block_number))
        response_id = self.send_request(self.get_request("get_contract_logs",
                                                         [contract_id, block_num - 1, head_block_number]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]

        with this_dict(result):
            check_that("lenght response", len(result), equal_to(3))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'randon in [start, current_block]' to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_random_block_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=value_amount)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.log_info("get random_block number in [0, {}]".format(block_num))

        block_num = self.get_random_value(self, 0, block_num)
        lcc.log_info("random_block: {}".format(block_num))
        self.set_timeout_wait(10)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]
        lcc.set_step("Get contract logs from random_block '{}'-1, to head block '{}'".format(block_num,
                                                                                             head_block_number))
        response_id = self.send_request(self.get_request("get_contract_logs",
                                        [contract_id, block_num - 1, head_block_number]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]

        with this_dict(result):
            check_that("lenght response", len(result), equal_to(3))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from -1 block to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_incorrect_block_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier,
                                                 value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]
        lcc.set_step("Get contract logs from block -1, to head block '{}'".format(head_block_number))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, -1, head_block_number]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]

        with this_dict(result):
            check_that("lenght response", result, equal_to([]))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs outside the block")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_outside_the_block(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier,
                                                 value_amount=value_amount)
        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        # todo: check pref_block, why block-1 has logs?
        lcc.set_step("Get contract logs from block 0, to block before the current_block".format(block_num - 2))
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, block_num - 2]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]

        with this_dict(result):
            check_that("lenght response", result, equal_to([]))
