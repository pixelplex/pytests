# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, equal_to, is_not_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'set_pending_transaction_callback'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "set_pending_transaction_callback")
@lcc.suite("Check work of method 'set_pending_transaction_callback'", rank=1)
class SetPendingTransactionCallback(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc1))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'set_pending_transaction_callback'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Set pending transaction callback and get response")
        response_id = self.send_request(self.get_request("set_pending_transaction_callback", [subscription_callback_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.set_step("Check set subscribe callback")
        check_that("'subscribe callback'", response["result"], is_none())

        lcc.set_step("Broadcast transfer operation and get notice")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                         to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0])
        check_that("notice", notice, is_not_none(), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "set_pending_transaction_callback")
@lcc.suite("Positive testing of method 'set_pending_transaction_callback'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc1))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check 'set_pending_transaction_callback' with perform transfer operation")
    @lcc.depends_on("DatabaseApi.SetPendingTransactionCallback.SetPendingTransactionCallback.method_main_check")
    def check_notice_of_pending_transaction_callback_with_transfer_operation(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Set pending transaction callback and get response")
        response_id = self.send_request(self.get_request("set_pending_transaction_callback", [subscription_callback_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.set_step("Check set subscribe callback")
        check_that("'subscribe callback'", response["result"], is_none())

        lcc.set_step("Broadcast transfer operation")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                         to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)

        lcc.set_step("Get notice about call contract and check notice of perform transfer operation")
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0])
        del broadcast_result["trx"]["operation_results"]
        check_that("notice params", notice, equal_to(broadcast_result["trx"]))

    @lcc.prop("type", "method")
    @lcc.test("Check 'set_pending_transaction_callback' with call contract operation")
    @lcc.depends_on("DatabaseApi.SetPendingTransactionCallback.SetPendingTransactionCallback.method_main_check")
    def check_notice_of_pending_transaction_callback_with_call_contract_operation(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id, notify_remove_create=False)

        lcc.set_step("Set pending transaction callback and get response")
        response_id = self.send_request(self.get_request("set_pending_transaction_callback", [subscription_callback_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.set_step("Check set subscribe callback")
        check_that("'subscribe callback'", response["result"], is_none())

        lcc.set_step("Create 'piggy' contract in ECHO network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier, need_broadcast_result=True)

        lcc.set_step("Call 'greet' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet,
                                                              callee=contract_id.get("contract_id"))
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.set_step("Get notice about call contract and check notice of call contract operation")
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0])
        del broadcast_result["trx"]["operation_results"]
        check_that("notice params", notice, equal_to(broadcast_result["trx"]))
