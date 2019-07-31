# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'broadcast_transaction_with_callback'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("network_broadcast_api", "broadcast_transaction_with_callback")
@lcc.suite("Check work of method 'broadcast_transaction_with_callback'", rank=1)
class BroadcastTransactionWithCallback(BaseTest):

    def __init__(self):
        super().__init__()
        self.__network_broadcast_identifier = None
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
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', network_broadcast='{}', registration='{}'".format(
                self.__database_api_identifier,
                self.__network_broadcast_identifier,
                self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'broadcast_transaction_with_callback'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        lcc.set_step("Get account balance before broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        account_balance = response["result"][0]["amount"]
        lcc.set_step("Broadcast transaction")
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback",
                                                         [subscription_callback_id, signed_tx.json()]),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)
        notice = self.get_notice(subscription_callback_id)
        lcc.set_step("Check that signed transaction in notice")
        del notice["trx"]["signed_with_echorand_key"]
        del notice["trx"]["operation_results"]
        check_that("transaction", signed_tx.json(), equal_to(notice["trx"]))
        lcc.set_step("Сheck that transaction has passed")
        check_that("'call method 'get_objects''", response["result"], is_none(), quiet=True)
        lcc.set_step("Get account balance after broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Check that account: '{}', with balance: '{}', get 1 asset".format(self.echo_acc1,
                                                                                        account_balance))
        account_balance_current = response["result"][0]["amount"]
        check_that("account_balance", account_balance + 1, equal_to(account_balance_current))
