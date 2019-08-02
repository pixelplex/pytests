# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, this_dict, check_that_entry, equal_to, is_str, has_length, \
    require_that, is_true, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'subscribe_contract_logs'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "subscribe_contract_logs")
@lcc.suite("Check work of method 'subscribe_contract_logs'", rank=1)
class SubscribeContractLogs(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")

    def get_head_block_number(self):
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        lcc.log_info("head block number: {}".format(head_block_number))
        return head_block_number

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
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'subscribe_contract_logs'")
    def method_main_check(self, get_random_integer, get_random_integer_up_to_ten):
        subscription_callback_id = get_random_integer
        value_amount = get_random_integer_up_to_ten
        _from = 0

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=value_amount)

        lcc.set_step("Get the head_block number")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Subscribe to created contract")
        params = [subscription_callback_id, contract_id, _from, head_block_number]
        response_id = self.send_request(self.get_request("subscribe_contract_logs", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"]:
            raise Exception("Subscription to contract logs not issued")
        lcc.log_info("Subscription to contract logs successful")

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check subscribe contracts log")
        for log in contract_logs_notice:
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

        lcc.set_step("Get the head_block number")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get contract logs with 'to' param that equal to head_block_number")
        params = [contract_id, _from, head_block_number]
        response_id = self.send_request(self.get_request("get_contract_logs", params), self.__database_api_identifier)
        contract_logs = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contract_logs' with params: from='{}', to='{}'".format(_from, head_block_number))

        lcc.set_step("Check that responses from 'get_contract_logs' and 'subscribe_contract_logs' are equal")
        check_that("result", contract_logs, equal_to(contract_logs_notice), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "subscribe_contract_logs")
@lcc.suite("Positive testing of method 'subscribe_contract_logs'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "pennieReturned()")
        self.setAllValues_method_name = "setAllValues(uint256,string)"
        self.setString_method_name = "onStringChanged(string)"
        self.setUint256_method_name = "onUint256Changed(uint256)"
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.set_all_values = self.get_byte_code("dynamic_fields", self.setAllValues_method_name)

    @staticmethod
    def get_random_int(_from=0, _to=0):
        return random.randint(_from, _to)

    def get_head_block_number(self):
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        head_block_number = self.get_response(response_id)["result"]["head_block_number"]
        lcc.log_info("head block number: {}".format(head_block_number))
        return head_block_number

    def subscribe_contract_logs(self, callback, contract_id, _from, head_block_number):
        params = [callback, contract_id, _from, head_block_number]
        response_id = self.send_request(self.get_request("subscribe_contract_logs", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"]:
            raise Exception("Subscription to contract logs not issued")
        lcc.log_info("Subscription to contract logs successful")

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
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs in notices two identical contract calls")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notices_two_identical_contract_calls(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer
        _from = 0

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Get the head_block number")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id, _from, head_block_number)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("First: Get notices about updates of created contract")
        contract_logs_notice_1 = self.get_notice(subscription_callback_id)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Second: Get notices about updates of created contract")
        contract_logs_notice_2 = self.get_notice(subscription_callback_id)

        lcc.set_step("Check that first and second notices are the same")
        check_that(
            "'notices are the same'",
            contract_logs_notice_1 == contract_logs_notice_2,
            is_true()
        )

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs in notices contract call that make two different logs")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notice_contract_call_that_make_two_different_logs(self, get_random_integer,
                                                                                 get_random_string):
        subscription_callback_id = int_param = get_random_integer
        string_param = get_random_string
        _from = 0

        lcc.set_step("Create 'dynamic_fields' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.dynamic_fields_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Get the head_block number")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id, _from, head_block_number)

        lcc.set_step("Call method of dynamic_fields contract: 'set_all_values'")
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        method_params = int_param_code + string_param_code
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.set_all_values + method_params,
                                                              callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'set_all_values' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check contract logs in notice with several logs")
        for i, log in enumerate(contract_logs_notice):
            lcc.log_info("Check log#'{}'".format(i))
            with this_dict(log):
                contract_id_that_called = self.get_contract_id(log["address"], address_format=True, new_contract=False)
                require_that("contract_id", contract_id_that_called, equal_to(contract_id), quiet=True)
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
        for i in range(len(contract_logs_notice))[:-1]:
            check_that(
                "'addresses in contract call result are the same'",
                contract_logs_notice[i]["address"] == contract_logs_notice[i + 1]["address"],
                is_true()
            )

        lcc.set_step("Check contract log value in notice")
        method_names_in_keccak_std = [self.get_keccak_standard_value(self.setUint256_method_name),
                                      self.get_keccak_standard_value(self.setString_method_name)]
        for i, log in enumerate(contract_logs_notice):
            check_that("'log value'", log["log"][0], equal_to(method_names_in_keccak_std[i]), quiet=True)

        lcc.set_step("Check contract log data in notice")
        call_contract_params = [int_param, string_param]
        output_types = [int, str]
        log_data = self.get_contract_log_data(contract_logs_notice, output_types, log_format=True)
        for i, data in enumerate(log_data):
            lcc.log_info("Check data#'{}'".format(i))
            check_that("'converted 'data' from hex'", data, equal_to(call_contract_params[i]))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs in notices from 'first block' to more than 'head_block_number'")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notice_from_first_block_to_more_than_head_block_number(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer
        _from = 0
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Get the head_block number and make 'to' param more than it")
        _to = self.get_head_block_number() + get_random_integer
        lcc.log_info("More than 'head_block_number' number is '{}'".format(_to))

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id, _from, _to)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check contract logs in notice")
        require_that("'log in notice has value'", bool(contract_logs_notice), is_true(), quiet=True)
        for log in contract_logs_notice:
            if check_that("contract_logs in notice", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs in notice", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test(
        "Check contract logs in notices from 'random block in [first block, head_block_number]' to 'head_block_number'")
    @lcc.tags("Bug ECHO-1055")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notice_from_random_block_to_head_block_number(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Get the head_block number")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get random_block in [first block, head_block_number] interval")
        random_block_num = self.get_random_int(_to=head_block_number)
        lcc.log_info("random block number: {}".format(random_block_num))

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id, random_block_num, head_block_number)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check contract logs in notice")
        require_that("'log in notice has value'", bool(contract_logs_notice), is_true(), quiet=True)
        for log in contract_logs_notice:
            if check_that("contract_logs in notice", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs in notice", log, has_entry(key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs in notices from 'negative block number' to 'head_block_number'")
    @lcc.tags("Bug ECHO-1055")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notice_from_negative_block_number_to_head_block_number(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer
        contract_log_keys = ["address", "log", "data"]

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Get the head_block number")
        head_block_number = self.get_head_block_number()

        lcc.set_step("Get negative block number")
        negative_block_num = self.get_random_int(_to=get_random_integer) * -1
        lcc.log_info("negative block number: {}".format(negative_block_num))

        lcc.set_step("Subscribe to created contract")
        self.subscribe_contract_logs(subscription_callback_id, contract_id, negative_block_num, head_block_number)

        lcc.set_step("Call contract method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Method 'getPennie' performed successfully")

        lcc.set_step("Get notices about updates of created contract")
        contract_logs_notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check contract logs in notice")
        require_that("'log in notice has value'", bool(contract_logs_notice), is_true(), quiet=True)
        for log in contract_logs_notice:
            if check_that("contract_logs in notice", log, has_length(3)):
                for key in contract_log_keys:
                    require_that("contract_logs in notice", log, has_entry(key), quiet=True)


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "subscribe_contract_logs")
@lcc.suite("Negative testing of method 'subscribe_contract_logs'", rank=3)
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
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Call method with negative parameter 'to'")
    @lcc.tags("Bug: 'ECHO-1034'", "Bug ECHO-1055")
    @lcc.disabled()
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_in_notice_with_negative_parameter_to(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer
        _from = 0

        lcc.set_step("Create contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        lcc.set_step("Get negative block number")
        negative_block_num = self.get_random_int(_to=get_random_integer) * -1
        lcc.log_info("negative block number: {}".format(negative_block_num))

        lcc.set_step("Subscribe to created contract")
        params = [subscription_callback_id, contract_id, _from, negative_block_num]
        response_id = self.send_request(self.get_request("subscribe_contract_logs", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"]:
            raise Exception("Subscription to contract logs not issued")
        lcc.log_info("Subscription to contract logs successful")

        lcc.set_step("Check contract logs")
        check_that("'subscribe_contract_logs' return error message with '{}' params".format(params),
                   response, has_entry("error"), quiet=True)
