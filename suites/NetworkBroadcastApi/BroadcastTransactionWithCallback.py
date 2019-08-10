# -*- coding: utf-8 -*-
from copy import deepcopy

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none, is_true, is_false

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

    @staticmethod
    def get_trx_without_sign_info_from_notice(notice):
        trx = deepcopy(notice["trx"])
        del trx["signed_with_echorand_key"]
        del trx["operation_results"]
        return trx

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
    @lcc.test("Simple work of method 'broadcast_transaction_with_callback'")
    def method_main_check(self, get_random_integer, get_random_integer_up_to_ten):
        subscription_callback_id = get_random_integer
        transfer_amount = get_random_integer_up_to_ten

        lcc.set_step("Create signed transaction of transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                                  amount=transfer_amount, to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        lcc.log_info("Signed transaction of 'transfer_operation' created successfully")

        lcc.set_step("Get account balance before transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' in '{}' assets".format(self.echo_acc1, account_balance, self.echo_asset))

        lcc.set_step("Broadcast transaction")
        params = [subscription_callback_id, signed_tx]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'broadcast_transaction_with_callback'")

        lcc.set_step("Check simple work of method 'broadcast_transaction_with_callback'")
        check_that("'broadcast_transaction_with_callback' result", response["result"], is_none(), quiet=True)

        lcc.set_step("Get notice about broadcast transaction")
        notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check that signed transaction in notice")
        check_that("transaction", signed_tx, equal_to(self.get_trx_without_sign_info_from_notice(notice)), quiet=True)

        lcc.set_step("Get account balance after transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        updated_account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info(
            "'{}' account has '{}' in '{}' assets".format(self.echo_acc1, updated_account_balance, self.echo_asset))

        lcc.set_step("Check that transfer operation completed successfully")
        check_that("'account balance'", (updated_account_balance - account_balance) == transfer_amount, is_true(),
                   quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("network_broadcast_api", "broadcast_transaction_with_callback")
@lcc.suite("Positive testing of method 'broadcast_transaction_with_callback'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.breakPiggy = self.get_byte_code("piggy", "breakPiggy()")

        self.contract = self.get_byte_code("contract_create_contract", "code")
        self.deploy_contract = self.get_byte_code("contract_create_contract", "deploy_contract()")
        self.get_creator = self.get_byte_code("contract_create_contract", "created_contract")["creator()"]
        self.tr_asset_to_creator = self.get_byte_code("contract_create_contract", "created_contract")[
            "tr_asset_to_creator()"]

    @staticmethod
    def get_trx_without_sign_info_from_notice(notice):
        trx = deepcopy(notice["trx"])
        del trx["signed_with_echorand_key"]
        del trx["operation_results"]
        return trx

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
    @lcc.test("Check 'broadcast_transaction_with_callback' of call piggy contract operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransactionWithCallback.BroadcastTransactionWithCallback.method_main_check")
    def broadcast_call_piggy_contract_operation_with_callback(self, get_random_integer):
        subscription_callback_id = value_amount = get_random_integer

        lcc.set_step("Create 'piggy' contract in the Echo network and get it's contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=value_amount)

        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        destroy_status = self.get_response(response_id)['result'][0]['destroyed']
        lcc.set_step("Check that contract exists")
        check_that('contract destroy status', destroy_status, is_false())

        lcc.set_step("Call contract method breakPiggy")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.breakPiggy, callee=contract_id)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        lcc.log_info("Signed transaction of 'contract_call_operation' created successfully")

        lcc.set_step("Broadcast transaction")
        params = [subscription_callback_id, signed_tx]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that 'broadcast_transaction_with_callback' completed successfully")
        check_that("'broadcast_transaction_with_callback' result", response["result"], is_none(), quiet=True)

        lcc.set_step("Get notice about broadcast transaction")
        notice = self.get_notice(subscription_callback_id)

        lcc.set_step("Check that signed transaction in notice")
        check_that("transaction", signed_tx, equal_to(self.get_trx_without_sign_info_from_notice(notice)), quiet=True)

        lcc.set_step("Check that contract destroyed")
        response_id = self.send_request(self.get_request("get_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        destroy_status = self.get_response(response_id)['result'][0]['destroyed']
        check_that('contract destroy status', destroy_status, is_true())

    @lcc.prop("type", "method")
    @lcc.test("Check 'broadcast_transaction_with_callback' of call contract_create_contract operation")
    @lcc.tags("asd")
    #@lcc.depends_on("NetworkBroadcastApi.BroadcastTransactionWithCallback.BroadcastTransactionWithCallback.method_main_check")
    def broadcast_call_contract_operation_with_callback(self, get_random_integer):
        subscription_callback_id = get_random_integer

        lcc.set_step("Create 'contract_create_contract' contract in the Echo network using 'broadcast_transaction_with_callback'")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        params = [subscription_callback_id, signed_tx]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that 'broadcast_transaction_with_callback' completed successfully")
        check_that("'broadcast_transaction_with_callback' result", response["result"], is_none(), quiet=True)

        lcc.set_step("Get 'contract_id' from broadcast notice.")
        notice = self.get_notice(subscription_callback_id)
        contract_result = self.get_contract_result(notice, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Call 'deploy_contract' method using 'broadcast_transaction_with_callback'")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.deploy_contract, callee=contract_id)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        params = [subscription_callback_id, signed_tx]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that 'broadcast_transaction_with_callback' completed successfully")
        check_that("'broadcast_transaction_with_callback' result", response["result"], is_none(), quiet=True)

        lcc.set_step("Get 'created_contract_id' from notice.")
        notice = self.get_notice(subscription_callback_id)
        contract_result = self.get_contract_result(notice, self.__database_api_identifier)

        lcc.set_step("Get output with address of deployed contract")
        created_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(created_contract_id))

        lcc.set_step("Call 'get_creator' method of created contract using 'broadcast_transaction_with_callback'")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_creator, callee=created_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        params = [subscription_callback_id, signed_tx]
        response_id = self.send_request(self.get_request("broadcast_transaction_with_callback", params),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that 'broadcast_transaction_with_callback' completed successfully")
        check_that("'broadcast_transaction_with_callback' result", response["result"], is_none(), quiet=True)

        notice = self.get_notice(subscription_callback_id)

        contract_result = self.get_contract_result(notice, self.__database_api_identifier)
        lcc.set_step("Get output with address of contract creator")
        creator_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(creator_contract_id))

        check_that("contract_id", contract_id, equal_to(creator_contract_id))
