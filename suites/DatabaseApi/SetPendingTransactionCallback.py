# -*- coding: utf-8 -*-
from copy import deepcopy

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

    def setup_test(self, test):
        lcc.set_step("Setup for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_test(self, test, status):
        lcc.set_step("Teardown for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")
        lcc.log_info("Test {}".format(status))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'set_pending_transaction_callback'")
    def method_main_check(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Subscribe to pending transactions")
        response_id = self.send_request(
            self.get_request("set_pending_transaction_callback", [subscription_callback_id]),
            self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check simple work of method 'set_pending_transaction_callback'")
        check_that("'subscribe callback'", response["result"], is_none())

        lcc.set_step("Perform transfer operation")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                         to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("Transfer operation performed successfully")

        lcc.set_step("Get notices about pending transaction")
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0], log_response=False)

        lcc.set_step("Check subscribe pending transaction")
        check_that("'notice about pending transaction'", notice, is_not_none(), quiet=True)


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
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def subscribe_pending_transactions(self, callback):
        response_id = self.send_request(
            self.get_request("set_pending_transaction_callback", [callback]), self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"] is not None:
            raise Exception("Subscription to pending transactions not issued")
        lcc.log_info("Subscription to pending transactions successful")

    @staticmethod
    def get_trx_from_broadcast_result(broadcast_result):
        trx = deepcopy(broadcast_result["trx"])
        del trx["operation_results"]
        return trx

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

    def setup_test(self, test):
        lcc.set_step("Setup for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_test(self, test, status):
        lcc.set_step("Teardown for '{}'".format(str(test).split(".")[-1]))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")
        lcc.log_info("Test {}".format(status))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check work of method with perform transfer operation")
    @lcc.depends_on("DatabaseApi.SetPendingTransactionCallback.SetPendingTransactionCallback.method_main_check")
    def check_notice_about_pending_transfer_transaction(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Subscribe to pending transactions")
        self.subscribe_pending_transactions(subscription_callback_id)

        lcc.set_step("Perform transfer operation")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                         to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Transfer operation performed successfully")

        lcc.set_step("Get notice about call contract and check notice of perform transfer operation")
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0])

        check_that("'notice about pending transfer transaction'", notice,
                   equal_to(self.get_trx_from_broadcast_result(broadcast_result)), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check work of method with perform contract operations")
    @lcc.depends_on("DatabaseApi.SetPendingTransactionCallback.SetPendingTransactionCallback.method_main_check")
    def check_notice_about_pending_contract_transactions(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Subscribe to pending transactions")
        self.subscribe_pending_transactions(subscription_callback_id)

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.piggy_contract)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Create contract operation performed successfully")

        lcc.set_step("Get notices about pending create contract transaction")
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0])

        lcc.set_step("Check notices about pending create contract transaction")
        check_that("'notice about pending create contract transaction'", notice,
                   equal_to(self.get_trx_from_broadcast_result(broadcast_result)), quiet=True)

        lcc.set_step("Get created 'piggy' contract id")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)
        lcc.log_info("Created 'piggy' contract id: '{}'".format(contract_id))

        lcc.set_step("Call contract method greet")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Method 'greet' performed successfully")

        lcc.set_step("Get notices about pending call contract transaction")
        notice = self.get_notice(subscription_callback_id, operation_id=operation[0])

        lcc.set_step("Check notices about pending call contract transaction")
        check_that("'notice about pending call contract transaction'", notice,
                   equal_to(self.get_trx_from_broadcast_result(broadcast_result)), quiet=True)
