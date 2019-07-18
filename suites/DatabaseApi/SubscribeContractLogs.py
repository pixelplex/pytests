# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, this_dict, check_that_entry,\
    equal_to, is_list, is_str, not_equal_to

from common.base_test import BaseTest

from echopy import Echo

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
        self.greet = self.get_byte_code("piggy", "greet")
        self.getPennie = self.get_byte_code("piggy", "getPennie")

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

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
    @lcc.test("Simple work of method 'subscribe_contract_logs'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                 self.__database_api_identifier, value_amount=10)
        lcc.set_step("Get 'head_block_number'")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contract_logs", [subscription_callback_id,
                                                                                     contract_id, 0,
                                                                                     head_block_number]),
                                        self.__database_api_identifier, debug_mode=False)
        response = self.get_response(response_id, log_response=False)

        lcc.set_step("Call 'getPennie' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id)
        notice_log_info = notice[0]
        lcc.set_step("Check subscribe contracts log")
        with this_dict(notice_log_info):
            check_that("lenght contract logs", len(notice_log_info), equal_to(3))
            contract_id_from_address = self.get_contract_from_address(self, notice_log_info["address"])
            check_that("contract_id", contract_id, equal_to(contract_id_from_address))
            check_that_entry("log", is_list(), quiet=True)
            if not self.validator.is_hex(notice_log_info["log"][0]):
                lcc.log_error("Wrong format of 'address', got: {}".format(notice_log_info["log"][0]))
            else:
                lcc.log_info("'address' has correct format: hex")
            check_that_entry("data", is_str())
        lcc.set_step("Check that contract log and subscribe contract logs are equal")
        response_id = self.send_request(self.get_request("get_contract_logs", [contract_id, 0, head_block_number +
                                                                               get_random_integer]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=False)["result"][0]
        check_that("result", response, equal_to(notice_log_info))


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "subscribe_contract_logs")
@lcc.suite("Positive testing of method 'subscribe_contract_logs'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
        self.getPennie = self.get_byte_code("piggy", "getPennie")
        self.setAllValues_method_name = "setAllValues(uint256,string)"
        self.setString_method_name = "onStringChanged(string)"
        self.setUint256_method_name = "onUint256Changed(uint256)"
        self.contract_dynamic_fields = self.get_byte_code("dynamic_fields", "code")
        self.set_all_values = self.get_byte_code("dynamic_fields", self.setAllValues_method_name)
        self.echo = Echo()

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

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
    @lcc.test("Check contract logs of two identical contracts")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_of_two_identical_contracts(self, get_random_integer):
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=10)

        lcc.set_step("Get 'head_block_number'")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contract_logs", [subscription_callback_id,
                                                                                     contract_id, 0,
                                                                                     head_block_number + get_random_integer]),
                                        self.__database_api_identifier, debug_mode=False)
        response = self.get_response(response_id, log_response=False)

        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id)
        notice_first_log_info = notice[0]

        lcc.set_step("Recall contract to have two identical logs")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)

        notice = self.get_notice(subscription_callback_id)
        notice_second_log_info = notice[0]

        lcc.set_step("Check that first and second subscribe contracts log are equal and has lenght 3")
        check_that("lenght of notice contract logs", len(notice_first_log_info), equal_to(3))
        check_that("contract_log", notice_first_log_info, equal_to(notice_second_log_info))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs of two different contracts")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_of_two_different_contracts(self, get_random_integer, get_random_string):
        int_param = subscription_callback_id = get_random_integer
        string_param = get_random_string
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_dynamic_fields_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_dynamic_fields,
                                                                self.__database_api_identifier)

        lcc.set_step("Get 'head_block_number'")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request(
            "subscribe_contract_logs", [subscription_callback_id,
                                        contract_dynamic_fields_id, 0,
                                        head_block_number + get_random_integer]),
                                        self.__database_api_identifier, debug_mode=False)
        response = self.get_response(response_id, log_response=False)

        lcc.set_step("Call method 'set_uint' and 'set_string")
        int_param_code = self.get_byte_code_param(int_param, param_type=int)
        string_param_code = self.get_byte_code_param(string_param, param_type=str, offset="40")
        bytecode = self.set_all_values + int_param_code + string_param_code
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)

        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)

        lcc.set_step("Get notices about updates of created contract")
        notice_log_info = self.get_notice(subscription_callback_id)
        call_contact_log0 = notice_log_info[0]
        call_contract_log1 = notice_log_info[1]

        lcc.set_step("Check subscribe on two different contracts log")
        check_that("contract_log", call_contact_log0, not_equal_to(call_contract_log1))
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

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from 'start' to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_from_start_to_head_block_number(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=10)

        lcc.set_step("Get 'head_block_number'")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contract_logs", [subscription_callback_id,
                                                                                     contract_id, 0,
                                                                                     head_block_number + get_random_integer]),
                                        self.__database_api_identifier, debug_mode=False)
        response = self.get_response(response_id, log_response=False)

        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

        notice = self.get_notice(subscription_callback_id)
        notice_log_info = notice[0]

        lcc.set_step("Check if lenght of contract logs is 3")
        with this_dict(notice_log_info):
            check_that("lenght of notice contract logs", len(notice_log_info), equal_to(3))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs from -1 block to 'head_block_number'")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_from_incorrect_block_to_head_block_number(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=10)

        lcc.set_step("Get 'head_block_number'")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contract_logs", [subscription_callback_id,
                                                                                     contract_id, -1,
                                                                                     head_block_number + get_random_integer]),
                                        self.__database_api_identifier, debug_mode=False)
        self.get_response(response_id, log_response=False)

        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)
        notice = self.get_notice(subscription_callback_id)
        notice_log_info = notice[0]

        # todo: check lenght of notice info. Bug: ECHO-1055
        lcc.set_step("Check if lenght of contract logs is 3")
        with this_dict(notice_log_info):
            check_that("lenght of notice contract logs", len(notice_log_info), equal_to(3))

    @lcc.prop("type", "method")
    @lcc.test("Check contract logs outside blocks")
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_outside_blocks(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=10)

        lcc.set_step("Get 'head_block_number'")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        head_block_number = response["head_block_number"]

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contract_logs", [subscription_callback_id,
                                                                                     contract_id, 0,
                                                                                     head_block_number - 1]),
                                        self.__database_api_identifier, debug_mode=False)
        self.get_response(response_id, log_response=False)

        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)
        notice = self.get_notice(subscription_callback_id)
        notice_log_info = notice[0]

        # todo: check notice (notice must be 0). Bug: ECHO-1055
        lcc.set_step("Check if lenght of contract logs is 3")
        with this_dict(notice_log_info):
            check_that("lenght of notice contract logs", len(notice_log_info), equal_to(3))


@lcc.prop("testing", "negative")
@lcc.tags("database_api", "subscribe_contract_logs")
@lcc.suite("Negative testing of method 'subscribe_contract_logs'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
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
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Call method with 'to block' equal to -1")
    @lcc.tags("Bug: 'ECHO-1034'")
    @lcc.disabled()
    @lcc.depends_on("DatabaseApi.SubscribeContractLogs.SubscribeContractLogs.method_main_check")
    def check_contract_logs_with_negative_block_number(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, value_amount=10)

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contract_logs", [subscription_callback_id,
                                                                                     contract_id, 0,
                                                                                     -1]),
                                        self.__database_api_identifier, debug_mode=False)
        self.get_response(response_id, log_response=False)

        lcc.set_step("Call contracts method getPennie")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.getPennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)
        notice = self.get_notice(subscription_callback_id)
        notice_log_info = notice[0]

        lcc.set_step("Check if lenght of contract logs is 3")
        with this_dict(notice_log_info):
            check_that("lenght of notice contract logs", len(notice_log_info), equal_to([]))
