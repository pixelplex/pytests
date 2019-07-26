# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'broadcast_transaction'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("network_broadcast_api", "broadcast_transaction")
@lcc.suite("Check work of method 'broadcast_transaction'", rank=1)
class BroadcastTransaction(BaseTest):

    def __init__(self):
        super().__init__()
        self.__network_broadcast_identifier = None
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
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
    @lcc.test("Simple work of method 'broadcast_transaction'")
    def method_main_check(self):
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
        response_id = self.send_request(self.get_request("broadcast_transaction",
                                                         [signed_tx.json()]),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)
        lcc.set_step("Сheck that transaction has passed")
        check_that("'call method 'get_objects''", response["result"], is_none(), quiet=True)
        lcc.set_step("Get account balance after broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Check that account: '{}', with balance: '{}', get 1 asset".format(self.echo_acc1, account_balance))
        account_balance_current = response["result"][0]["amount"]
        check_that("account_balance", account_balance + 1, equal_to(account_balance_current))
