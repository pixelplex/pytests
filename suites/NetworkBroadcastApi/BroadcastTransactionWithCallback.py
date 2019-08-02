# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'broadcast_transaction_with_callback'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("network_broadcast_api", "broadcast_transaction_with_callback")
@lcc.suite("Check work of method 'broadcast_transaction_with_callback'", rank=1)
class BroadcastTransactionWithCallback(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
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
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier,
                self.__network_broadcast_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'broadcast_transaction_with_callback'")
    def method_main_check(self, get_random_integer, get_random_integer_up_to_ten):
        transfer_amount = get_random_integer_up_to_ten

        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create signed transaction of transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  amount=transfer_amount,
                                                                  to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)

        lcc.set_step("Get account balance before transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' in '{}' assets".format(self.echo_acc1, account_balance, self.echo_asset))

        lcc.set_step("Broadcast transaction")
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback",
                                                         [subscription_callback_id, signed_tx.json()]),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Get notice of 'broadcast_transaction_with_callback'")
        notice = self.get_notice(subscription_callback_id)

        del notice["trx"]["signed_with_echorand_key"]
        del notice["trx"]["operation_results"]

        lcc.set_step("Check that signed transaction in notice")
        check_that("transaction", signed_tx.json(), equal_to(notice["trx"]))

        lcc.set_step("Сheck that transaction has passed")
        check_that("'call method 'get_objects''", response["result"], is_none(), quiet=True)

        lcc.set_step("Get account balance after transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        updated_account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info(
            "'{}' account has '{}' in '{}' assets".format(self.echo_acc1, updated_account_balance, self.echo_asset))

        lcc.set_step("Check that transfer operation completed successfully")
        check_that("'account balance'", (updated_account_balance - account_balance) == transfer_amount, is_true(),
                   quiet=True)
