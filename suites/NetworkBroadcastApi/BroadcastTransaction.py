# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none, is_not_none, not_equal_to

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

@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "broadcast_transaction")
@lcc.suite("Positive testing of method 'broadcast_transaction'", rank=2)
class PositiveTesting(BaseTest):

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

    def broadcast_trx(self, operation):
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        lcc.set_step("Broadcast transaction")
        response_id = self.send_request(self.get_request("broadcast_transaction",
                                                         [signed_tx.json()]),
                                        self.__network_broadcast_identifier)
        return self.get_response(response_id)

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with account_create_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_created_account(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name
        public_key = self.generate_keys()
        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that("'get_account_by_name' response", response["result"], is_none())
        operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key[1], public_key[1],
                                                               registrar=self.echo_acc0, signer=self.echo_acc0)
        response = self.broadcast_trx(operation)

        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that("'get_account_by_name' response", response["result"], is_not_none(), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with account_update_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_account_update_operation(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Registration an account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.set_step("Get info about account and store current 'delegating_account'")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        current_delegating_account = response["result"][0]["options"]["delegating_account"]
        lcc.log_info("Current delegating account of '{}' is '{}'".format(new_account, current_delegating_account))

        lcc.set_step("Add assets to a new account to pay a fee")
        old_options = response["result"][0]["options"]
        operation = self.echo_ops.get_account_update_operation(echo=self.echo, account=new_account,
                                                               voting_account=old_options["voting_account"],
                                                               delegating_account=self.echo_acc0,
                                                               num_committee=old_options["num_committee"],
                                                               votes=old_options["votes"])

        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Perform 'account_update_operation' to change delegating_account")
        response = self.broadcast_trx(operation)
        lcc.log_info("{}".format(response))

        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        delegating_account_after_broadcast = response["result"][0]["options"]["delegating_account"]
        check_that("delegating_account", current_delegating_account, not_equal_to(delegating_account_after_broadcast))
