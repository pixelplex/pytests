# -*- coding: utf-8 -*-
import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none, is_not_none, not_equal_to, is_true, is_

from common.base_test import BaseTest
from project import EXECUTION_STATUS_PATH, INIT4_PK

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
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.state = None


    def check_status_file(self):
        self.state = True
        if not os.path.exists(EXECUTION_STATUS_PATH):
            with open(EXECUTION_STATUS_PATH, "w") as file:
                file.write(json.dumps({"broadcast_transaction_get_balance_objects": {"state": True, "passed": False}}))
        else:
            file = json.load(open(EXECUTION_STATUS_PATH, 'r'))
            if "broadcast_transaction_get_balance_objects" not in file.keys():
                f = open(EXECUTION_STATUS_PATH, 'w')
                file.update({"broadcast_transaction_get_balance_objects": {"state": True, "passed": False}})
                f.write(json.dumps(file))
                f.close()
            self.state = False

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        self.check_status_file()
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier,
                self.__network_broadcast_identifier))
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
    def method_main_check(self, get_random_integer_up_to_ten):
        transfer_amount = get_random_integer_up_to_ten

        lcc.set_step("Create signed transaction of transfer operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1, amount=transfer_amount)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, no_broadcast=True)
        lcc.log_info("Signed transaction of transfer operation created successfully")

        lcc.set_step("Get account balance before transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' in '{}' assets".format(self.echo_acc1, account_balance, self.echo_asset))

        lcc.set_step("Broadcast transaction")
        response_id = self.send_request(self.get_request("broadcast_transaction", [signed_tx]),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'broadcast_transaction'")

        lcc.set_step("Check that transaction broadcast")
        check_that("'broadcast_transaction' result", response["result"], is_none(), quiet=True)

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
        self.init4_account_name = "init4"
        self.state = None

    def read_execution_status(self):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        self.state = execution_status["broadcast_transaction_get_balance_objects"]["state"]

    def change_test_status(self):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        if execution_status["broadcast_transaction_get_balance_objects"]:
            execution_status["broadcast_transaction_get_balance_objects"]["state"] = False
            self.state = False
            with open(EXECUTION_STATUS_PATH, "w") as file:
                file.write(json.dumps(execution_status))
        else:
            self.state = False

    @staticmethod
    def add_log_info(log):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        execution_status["broadcast_transaction_get_balance_objects"]["state"] = False
        with open(EXECUTION_STATUS_PATH, "w") as file:
            execution_status["broadcast_transaction_get_balance_objects"].update({"passed": log})
            file.write(json.dumps(execution_status))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        self.read_execution_status()
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier, self.__registration_api_identifier,
                self.__network_broadcast_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    def broadcast_transaction(self, operation):
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        response_id = self.send_request(self.get_request("broadcast_transaction", [signed_tx]),
                                        self.__network_broadcast_identifier)
        self.get_response(response_id)

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with account_create_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_created_account(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name
        public_key = self.generate_keys()

        lcc.set_step("Check that account: {} doesn't exist in network".format(account_name))
        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        self.__database_api_identifier)
        response_result = self.get_response(response_id)["result"]
        check_that("'get_account_by_name' response", response_result, is_none())

        lcc.set_step("Create 'account_create_operation'")
        operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key[1], public_key[1],
                                                               registrar=self.echo_acc0, signer=self.echo_acc0)

        lcc.set_step("Sign transaction of 'account_create_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Check that account: {} created successfully".format(account_name))
        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        self.__database_api_identifier)
        response_result = self.get_response(response_id)["result"]
        check_that("'get_account_by_name' response", response_result, is_not_none(), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with account_update_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_account_update_operation(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get info about account and store current 'delegating_account'")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response_result_options = self.get_response(response_id)["result"][0]["options"]
        current_delegating_account = response_result_options["delegating_account"]
        lcc.log_info("Current delegating account of '{}' is '{}'".format(new_account, current_delegating_account))

        lcc.set_step("Create 'account_update_operation'")
        operation = self.echo_ops.get_account_update_operation(echo=self.echo, account=new_account,
                                                               voting_account=response_result_options["voting_account"],
                                                               delegating_account=self.echo_acc0,
                                                               num_committee=response_result_options["num_committee"],
                                                               votes=response_result_options["votes"])

        lcc.set_step("Add assets to a new account to pay fee for 'account_update_operation'")
        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.perform_transfer_operations(self, self.echo_acc0, new_account,
                                               self.__database_api_identifier, transfer_amount=fee)
        lcc.log_info("Needed amount '{}' to pay fee added to account '{}'".format(fee, new_account))

        lcc.set_step("Sign transaction of 'account_update_operation' and broadcast")
        self.broadcast_transaction(operation)

        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        delegating_account_after_broadcast = self.get_response(response_id)["result"][0]["options"]["delegating_account"]

        lcc.set_step("Check that delegating_account changed after broadcast 'account_update_operation'")
        check_that("delegating_account", current_delegating_account, not_equal_to(delegating_account_after_broadcast))

# todo: add operations "account_whitelist", "account_transfer"

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with asset_create_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_asset_create_operation(self, get_random_valid_account_name, get_random_valid_asset_name):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name
        operation_count = 1

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create 'asset_create_operation'")
        operation = self.echo_ops.get_asset_create_operation(echo=self.echo, issuer=new_account,
                                                             symbol=new_asset_name)

        lcc.set_step("Add balance to pay fee for 'asset_create_operation'")
        self.utils.add_balance_for_operations(self, new_account, operation,
                                              self.__database_api_identifier,
                                              operation_count=operation_count,
                                              log_broadcast=True)
        lcc.log_info("Balance added  to account: '{},".format(new_account))

        lcc.set_step("Sign transaction of 'asset_create_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Check that new asset created")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [[new_asset_name]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        if not self.validator.is_asset_id(response["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(response["id"]))
        else:
            lcc.log_info("'id' has correct format: asset_id")
        check_that("asset symbol", response["symbol"], equal_to(new_asset_name))

# todo: add operations "asset_update", "asset_update_bitasset", "asset_update_feed_producers"

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with asset_issue_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_asset_issue_operation(self, get_random_valid_asset_name, get_random_valid_account_name):
        new_asset = get_random_valid_asset_name
        account_names = get_random_valid_account_name
        asset_value = 100
        lcc.set_step("Create asset and get id new asset")
        new_asset = self.utils.get_asset_id(self, new_asset, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset))

        lcc.set_step("Create new account")
        account_id = self.get_account_id(account_names, self.__database_api_identifier,
                                         self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.set_step("Create 'asset_issue_operation'")
        operation = self.echo_ops.get_asset_issue_operation(echo=self.echo, issuer=self.echo_acc0,
                                                            value_amount=asset_value, value_asset_id=new_asset,
                                                            issue_to_account=account_id)

        lcc.set_step("Sign transaction of 'asset_issue_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Get account balances")
        response_id = self.send_request(self.get_request("get_account_balances", [account_id, [new_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        lcc.set_step("Check that account: {} get assets".format(account_id))
        check_that("amount", response["amount"], equal_to(asset_value))

# todo: add operations "asset_reserve", "asset_fund_fee_pool", "asset_publish_feed", "proposal_create", "proposal_update", "proposal_delete"

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with committee_member_create_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_committee_member_create_operation(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name

        lcc.set_step("Create new account")
        account_id = self.get_account_id(account_name, self.__database_api_identifier,
                                         self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.set_step("Get eth address")
        self.utils.perform_sidechain_eth_create_address_operation(self, account_id, self.__database_api_identifier)
        eth_account_address = self.utils.get_eth_address(self, account_id,
                                                         self.__database_api_identifier)["result"]["eth_addr"]

        lcc.set_step("Create 'committee_member_create_operation'")
        operation = self.echo_ops.get_committee_member_create_operation(echo=self.echo,
                                                                        committee_member_account=account_id,
                                                                        eth_address=eth_account_address,
                                                                        url="test_url")

        lcc.set_step("Add balance to pay fee for 'get_committee_member_create_operation'")
        self.utils.add_balance_for_operations(self, account_id, operation, self.__database_api_identifier,
                                              log_broadcast=False)

        lcc.set_step("Sign transaction of 'committee_member_create_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Check that account become committee member")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", [account_name, 1]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0][0]
        check_that("account_name", account_name, equal_to(response))

# todo: add operations "committee_member_update", "committee_member_update_global_parameters"

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with vesting_balance_create_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_vesting_balance_create_operation(self, get_random_valid_asset_name, get_random_integer,
                                                   get_random_valid_account_name):
        new_asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name

        lcc.set_step("Create asset and get new asset id")
        new_asset = self.utils.get_asset_id(self, new_asset, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset))

        lcc.set_step("Add created assets to account")
        self.utils.add_assets_to_account(self, new_asset_amount, new_asset, self.echo_acc0,
                                         self.__database_api_identifier)

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create 'vesting_balance_create_operation'")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=new_account, amount=new_asset_amount,
                                                                       amount_asset_id=new_asset)

        lcc.set_step("Sign transaction of 'vesting_balance_create_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Get created account 'vesting_balance'")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balances_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]

        lcc.set_step("Check that vesting balance equal to asset amount")
        check_that("id", vesting_balances_amount, equal_to(new_asset_amount))

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with vesting_balance_withdraw_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_vesting_balance_withdraw_operation(self, get_random_valid_asset_name, get_random_integer,
                                                     get_random_valid_account_name):
        asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name
        vesting_cliff_seconds = 10

        lcc.set_step("Create asset and get new asset id")
        new_asset = self.utils.get_asset_id(self, new_asset, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset))

        lcc.set_step("Add created assets to account")
        self.utils.add_assets_to_account(self, asset_amount, new_asset, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.log_info("Created '{}' assets added to '{}' account successfully".format(new_asset, self.echo_acc0))

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get 'global_datetime'")
        datetime = self.get_datetime(global_datetime=True)
        lcc.log_info("global_datetime: {}".format(datetime))

        lcc.set_step("Broadcast 'vesting_balance_create_operation', add balance to pay fee and store vesting balance id")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=new_account, amount=asset_amount,
                                                                       amount_asset_id=new_asset,
                                                                       begin_timestamp=datetime,
                                                                       vesting_cliff_seconds=vesting_cliff_seconds,
                                                                       vesting_duration_seconds=0)
        self.utils.add_balance_for_operations(self, new_account, operation, self.__database_api_identifier,
                                              log_broadcast=False)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("vesting balance id: {}".format(vesting_balance_id))

        self.set_timeout_wait(vesting_cliff_seconds)

        lcc.set_step("Create 'vesting_balance_withdraw_operation'")
        operation = self.echo_ops.get_vesting_balance_withdraw_operation(echo=self.echo,
                                                                         vesting_balance=vesting_balance_id,
                                                                         owner=new_account, amount=asset_amount,
                                                                         amount_asset_id=new_asset)
        lcc.set_step("Add balance to pay fee for 'vesting_balance_withdraw_operation'")
        self.utils.add_balance_for_operations(self, new_account, operation, self.__database_api_identifier,
                                              log_broadcast=False)

        lcc.set_step("Sign transaction of 'vesting_balance_withdraw_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Check that balance was withdrawn")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balances_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("vesting_balances_amount", vesting_balances_amount, equal_to(0))

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with balance_claim_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_balance_claim_operation(self, get_random_valid_account_name):
        if self.state:
            lcc.set_step("Get account id and public key and store")
            account_info = self.get_account_by_name(self.init4_account_name, self.__database_api_identifier)
            account_id = account_info["result"]["id"]
            public_key = account_info["result"]["echorand_key"]
            lcc.log_info(
                "'{}' account has id='{}' and public_key='{}'".format(self.init4_account_name, account_id,
                                                                      public_key))

            lcc.set_step("Get balance objects before balance claim operation and store balance id and amount")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"][0]
            balance_id = result["id"]
            balance_amount = int(result["balance"]["amount"])
            lcc.log_info(
                "'{}' account has balance with id='{}' and amount='{}'".format(self.init4_account_name, balance_id,
                                                                               balance_amount))

            lcc.set_step("Create 'balance_claim_operation'")
            operation = self.echo_ops.get_balance_claim_operation(echo=self.echo, deposit_to_account=account_id,
                                                                  balance_owner_public_key=public_key,
                                                                  value_amount=balance_amount,
                                                                  balance_owner_private_key=INIT4_PK,
                                                                  balance_to_claim=balance_id)

            lcc.set_step("Sign transaction of 'balance_claim_operation' and broadcast")
            self.broadcast_transaction(operation)
            self.change_test_status()

            lcc.set_step("Get balance objects after balance claim operation")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            lcc.log_info("update execution_status parameter ")
            self.add_log_info(False)
            result = self.get_response(response_id)["result"]

            lcc.set_step("Check response from 'get_balance_objects' method after balance claim operation")
            if check_that("balance", result, is_([])):
                self.add_log_info(True)
        else:
            execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))["get_balance_objects"]
            if execution_status["passed"]:
                lcc.log_info("Testing of the 'balance_claim_operation' method was successfully completed earlier")
            else:
                lcc.log_error("Test of method 'balance_claim_operation' failed during the previous run. "
                              "Can not claim initial balance again. To run test again please run a clean node.")



# # todo: add operations: "override_transfer", "asset_claim_fees"

# contract_create_operation
# contract_call_operation
# contract_transfer_operation
# # todo: add operations: "sidechain_change_config",
# account_address_create_operation
# # todo: add operations: "transfer_to_address",

# sidechain_eth_create_address_operation
# # todo: add operations: "sidechain_eth_approve_address",
# # todo: add operations: "sidechain_eth_deposit",
# sidechain_eth_withdraw_operation
# # todo: add operations: "sidechain_eth_approve_withdraw",

# contract_fund_pool_operation
# contract_whitelist_operation
# sidechain_eth_issue_operation
# sidechain_eth_burn_operation
# sidechain_erc20_register_token_operation
# # todo: add operations: "sidechain_erc20_deposit_token",

# sidechain_erc20_withdraw_token_operation
# # todo: add operations: "sidechain_erc20_approve_token_withdraw2",

# contract_update_operation
# # todo: add operations: "balance_claim",



