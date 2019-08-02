# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, equal_to, is_str, check_that, has_entry, has_length, \
    require_that, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_logs'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract_logs")
@lcc.suite("Check work of method 'get_contract_logs'", rank=1)
class GetContractLogs(BaseTest):

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

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_logs'")
    def method_main_check(self, get_random_integer_up_to_ten):
        value_amount = get_random_integer_up_to_ten
        _from = 0

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy, self.__database_api_identifier,
                                                 value_amount=value_amount)

        lcc.set_step("Call contract method getPennie and get trx block number")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.log_info("Method 'getPennie' performed successfully, block_num: '{}'".format(block_num))

        lcc.set_step("Get contract logs from '{}' block to current_block '{}'".format(_from, block_num))
        params = [contract_id, _from, block_num]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        response = self.get_response(response_id)
        logs = response["result"]
        lcc.log_info("Call method 'get_contract_logs' with params: '{}'".format(params))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(logs), is_true(), quiet=True)
        for log in logs:
            with this_dict(log):
                if check_that("contract_log", log, has_length(3)):
                    contract_id_that_called = self.get_contract_id(log["address"], address_format=True,
                                                                   new_contract=False)
                    require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
                    log_values = log["log"]
                    for log_value in log_values:
                        if not self.validator.is_hex(log_value):
                            lcc.log_error("Wrong format of 'log_value', got: {}".format(log_value))
                        else:
                            lcc.log_info("'log_value' has correct format: hex")
                    check_that_entry("data", is_str(), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_contract_logs")
@lcc.suite("Positive testing of method 'get_contract_logs'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.set_all_values = self.get_byte_code("dynamic_fields", "setAllValues(uint256,string)")

    @staticmethod
    def get_random_int(_from=0, _to=0):
        return random.randint(_from, _to)

    def get_head_block_number(self):
        self.set_timeout_wait(wait_block_count=1)
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        lcc.log_info("head block number: {}".format(head_block_number))
        return head_block_number

    def get_contract_logs(self, contract_id=None, _from=None, _to=None, params=None):
        if params is None:
            params = [contract_id, _from, _to]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        return self.get_response(response_id)["result"]

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
    @lcc.test("Check contract logs two identical contract calls")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_two_identical_contract_calls(self, get_random_integer):
        value_amount = get_random_integer
        call_count, _from, block_num = 2, 0, 0

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie two times and get trx block number")
        for i in range(call_count):
            operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                  bytecode=self.getPennie, callee=contract_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            block_num = broadcast_result["block_num"]
            lcc.log_info("Method #'{}' 'getPennie' performed successfully, block_num: '{}'".format(i, block_num))

        lcc.set_step("Get contract logs after two identical contract calls")
        params = [contract_id, _from, block_num]
        get_contract_logs_results = self.get_contract_logs(params=params)
        lcc.log_info("Call method 'get_contract_logs' with params: '{}'".format(params))

        lcc.set_step("Check contract logs two identical contract calls")
        require_that("'log has value'", bool(get_contract_logs_results), is_true(), quiet=True)
        for i in range(len(get_contract_logs_results))[:-1]:
            check_that(
                "'contract logs two identical contract calls are the same'",
                get_contract_logs_results[i] == get_contract_logs_results[i + 1],
                is_true()
            )

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs contract call that make two different logs")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_contract_call_that_make_two_different_logs(self, get_random_integer, get_random_string):
        int_param = get_random_integer
        string_param = get_random_string
        _from = 0

        lcc.set_step("Create 'dynamic_fields' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.dynamic_fields_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Call method of dynamic_fields contract: 'set_all_values'")
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        method_params = int_param_code + string_param_code
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.set_all_values + method_params,
                                                              callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        block_num = broadcast_result["block_num"]
        lcc.log_info("Method 'set_all_values' performed successfully, block_num: '{}'".format(block_num))

        lcc.set_step("Get contract logs after two different contract calls")
        params = [contract_id, _from, block_num]
        get_contract_logs_results = self.get_contract_logs(params=params)
        lcc.log_info("Call method 'get_contract_logs' with params: '{}'".format(params))

        lcc.set_step("Check contract logs contract call that make two different logs")
        require_that("'log has value'", bool(get_contract_logs_results), is_true(), quiet=True)
        for i in range(len(get_contract_logs_results))[:-1]:
            check_that(
                "'contract logs are not the same'",
                get_contract_logs_results[i] != get_contract_logs_results[i + 1],
                is_true()
            )

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from first block to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_first_block_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        _from = 0
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get the head_block number of the next block")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs with 'to' param that equal to head_block_number")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, _to=head_block_number)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(_from, head_block_number))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        for log in contract_logs:
            if check_that("contract_logs", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from first block to 'current_block'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_first_block_to_current_block(self, get_random_integer):
        value_amount = get_random_integer
        _from = 0
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        # todo: remove '-1'. Bug: ECHO-1032
        current_block_num = broadcast_result["block_num"] - 1
        lcc.log_info("Method 'getPennie' performed successfully, current_block_num is '{}'".format(current_block_num))

        lcc.set_step("Get contract logs with 'to' param that equal to current_block_num")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, _to=current_block_num)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(_from, current_block_num))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        for log in contract_logs:
            if check_that("contract_logs", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'current_block' to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_current_block_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        # todo: remove '-1'. Bug: ECHO-1032
        current_block_num = broadcast_result["block_num"] - 1
        lcc.log_info("Method 'getPennie' performed successfully, current_block_num is '{}'".format(current_block_num))

        lcc.set_step("Get the head_block number of the next block")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs with 'from' param is current_block_num, 'to' param is head_block_number")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=current_block_num, _to=head_block_number)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(current_block_num,
                                                                                              head_block_number))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        for log in contract_logs:
            if check_that("contract_logs", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'random block in [first block, current_block]' to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_random_block_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        # todo: remove '-1'. Bug: ECHO-1032
        current_block_num = broadcast_result["block_num"] - 1
        lcc.log_info("Method 'getPennie' performed successfully, current_block_num is '{}'".format(current_block_num))

        lcc.set_step("Get random_block in [first block, current_block] interval")
        random_block_num = self.get_random_int(_to=current_block_num)
        lcc.log_info("random block number: {}".format(random_block_num))

        lcc.set_step("Get the head_block number of the next block")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs with 'from' param is random_block, 'to' param is head_block_number")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=random_block_num, _to=head_block_number)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(random_block_num,
                                                                                              head_block_number))

        lcc.set_step("Check contract logs")
        require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        for log in contract_logs:
            if check_that("contract_logs", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'negative block number' to 'head_block_number'")
    @lcc.tags("Bug ECHO-1033")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_from_negative_block_number_to_head_block_number(self, get_random_integer):
        value_amount = get_random_integer
        # todo: uncomment. Bug ECHO-1033.
        # contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get negative block number")
        negative_block_num = self.get_random_int(_to=get_random_integer) * -1
        lcc.log_info("negative block number: {}".format(negative_block_num))

        lcc.set_step("Get the head_block number of the next block")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs with 'from' param is negative_block_number, 'to' param is head_block_number")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=negative_block_num, _to=head_block_number)
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(negative_block_num,
                                                                                              head_block_number))

        lcc.set_step("Check contract logs")
        # todo: remove. Bug ECHO-1033.
        check_that("contract_logs", contract_logs, equal_to([]))
        # todo: uncomment. Bug ECHO-1033.
        # require_that("'log has value'", bool(contract_logs), is_true(), quiet=True)
        # for log in contract_logs:
        #     if check_that("contract_logs", log, has_length(3)):
        #         for key in contract_log_keys:
        #             require_that("contract_logs", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'first block' to 'block before operation performed'")
    @lcc.tags("Bug ECHO-1033")
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_in_blocks_before_operation_performed(self, get_random_integer):
        value_amount = get_random_integer
        _from = 0

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        current_block_num = broadcast_result["block_num"]
        lcc.log_info("Method 'getPennie' performed successfully, current_block_num is '{}'".format(current_block_num))

        lcc.set_step("Get before current block number")
        before_current_block_num = self.get_random_int(_to=current_block_num)
        lcc.log_info("before current block number: {}".format(before_current_block_num))

        # todo: check previous block, why current_block-1 has logs? uncomment. Bug: ECHO-1032.
        # lcc.set_step("Get contract logs with 'to' param is current_block_num - 1")
        # _to = current_block_num - 1
        # contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, _to=_to)
        # lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(_from, _to))

        lcc.set_step("Get contract logs with 'to' param is before current block number")
        contract_logs = self.get_contract_logs(contract_id=contract_id, _from=_from, _to=before_current_block_num)
        lcc.log_info(
            "Call method 'get_contract_logs' with params: from='{}', to='{}'".format(_from, before_current_block_num))

        lcc.set_step("Check contract logs")
        check_that("contract_logs", contract_logs, equal_to([]))


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract_logs")
@lcc.suite("Negative testing of method 'get_contract_logs'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

    @staticmethod
    def get_random_int(_from=0, _to=0):
        return random.randint(_from, _to)

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
    @lcc.test("Call method with negative parameter 'to'")
    @lcc.tags("Bug: 'ECHO-1034'")
    @lcc.disabled()
    @lcc.depends_on("DatabaseApi.GetContractLogs.GetContractLogs.method_main_check")
    def check_contract_logs_with_negative_parameter_to(self, get_random_integer):
        value_amount = get_random_integer
        _from = 0

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get negative block number")
        negative_block_num = self.get_random_int(_to=get_random_integer) * -1
        lcc.log_info("negative block number: {}".format(negative_block_num))

        lcc.set_step("Get contract logs with 'to' param is negative block number")
        params = [contract_id, _from, negative_block_num]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        lcc.log_info(
            "Call method 'get_contract_logs' with params: from='{}', to='{}'".format(_from, negative_block_num))

        lcc.set_step("Check contract logs")
        check_that("'get_contract_logs' return error message with '{}' params".format(params),
                   response, has_entry("error"), quiet=True)
