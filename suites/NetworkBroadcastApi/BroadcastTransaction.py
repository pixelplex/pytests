# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_none, is_not_none, not_equal_to, is_true
from project import ACCOUNT_PREFIX
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
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__network_broadcast_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier,
                self.__registration_api_identifier,
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
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  amount=transfer_amount,
                                                                  to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        lcc.log_info("Signed transaction of transfer operation created successfully")

        lcc.set_step("Get account balance before transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        account_balance = self.get_response(response_id)["result"][0]["amount"]
        lcc.log_info("'{}' account has '{}' in '{}' assets".format(self.echo_acc1, account_balance, self.echo_asset))

        lcc.set_step("Broadcast transaction")
        response_id = self.send_request(self.get_request("broadcast_transaction",
                                                         [signed_tx.json()]),
                                        self.__network_broadcast_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Сheck that transaction broadcast")
        check_that("'broadcast_transaction' result", response["result"], is_none(), quiet=True)

        lcc.set_step("Get account balance after transfer transaction broadcast")
        response_id = self.send_request(self.get_request("get_account_balances",
                                                         [self.echo_acc1, [self.echo_asset]]),
                                        self.__database_api_identifier)
        updated_account_balance = self.get_response(response_id)["result"][0]["amount"]

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

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__network_broadcast_identifier = self.get_identifier("network_broadcast")

        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', network_broadcast='{}'".format(
                self.__database_api_identifier,
                self.__registration_api_identifier,
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
        response_id = self.send_request(self.get_request("broadcast_transaction",
                                                         [signed_tx.json()]),
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

# todo: add operations "limit_order_create", "limit_order_cancel", "call_order_update", "fill_order",

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with account_update_operation")
    @lcc.tags("asd")
    #@lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
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

        lcc.set_step("Add assets to a new account to pay fee and create 'account_upgrade_operation'")
        operation = self.echo_ops.get_account_update_operation(echo=self.echo, account=new_account,
                                                               voting_account=response_result_options["voting_account"],
                                                               delegating_account=self.echo_acc0,
                                                               num_committee=response_result_options["num_committee"],
                                                               votes=response_result_options["votes"])
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

# todo: add operation "account_whitelist"

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with account_upgrade_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_account_upgrade_operation(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Create new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create signed transaction of 'account_upgrade_operation'")
        operation = self.echo_ops.get_account_upgrade_operation(self.echo, account_to_upgrade=new_account,
                                                                upgrade_to_lifetime_member=True)

        lcc.set_step("Add balance to pay fee for 'account_upgrade_operation'")
        self.utils.add_balance_for_operations(self, new_account, operation, self.__database_api_identifier,
                                              log_broadcast=False)

        lcc.set_step("Sign transaction of 'account_upgrade_operation' and broadcast")
        self.broadcast_transaction(operation)

        lcc.set_step("Check that account become lifetime member")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response_result_lifetime_referrer = self.get_response(response_id)["result"][0]["lifetime_referrer"]
        check_that("'lifetime_referrer'", response_result_lifetime_referrer, equal_to(new_account))

# todo: add operation "account_transfer"

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

        lcc.set_step("Create signed transaction of 'asset_create_operation'")
        operation = self.echo_ops.get_asset_create_operation(echo=self.echo, issuer=new_account,
                                                             symbol=new_asset_name)

        lcc.set_step("Add balance to pay fee for 'asset_create_operation'")
        self.utils.add_balance_for_operations(self, new_account, operation,
                                              self.__database_api_identifier,
                                              operation_count=operation_count,
                                              log_broadcast=True)
        lcc.log_info("Balance added  to account: '{},".format(new_account))

        lcc.set_step("Broadcast asset create operation")
        self.broadcast_transaction(operation)

        lcc.set_step("Lookup asset symbols")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [[new_asset_name]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        lcc.set_step("Check that new asset created")
        lcc.log_info("{}".format(response))
        if not self.validator.is_asset_id(response["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(response["id"]))
        else:
            lcc.log_info("'id' has correct format: asset_id")
        check_that("asset symbol", response["symbol"], equal_to(new_asset_name))

# todo: add operations "asset_update", "asset_update_bitasset", "asset_update_feed_producers"

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with asset_issue_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_asset_issue_operation(self, get_random_valid_asset_name):
        asset_name = get_random_valid_asset_name
        account_names = ACCOUNT_PREFIX
        asset_value = 100
        lcc.set_step("Create asset and get id new asset")
        asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(asset_id))

        lcc.set_step("Create new account")
        account_id = self.get_account_id(account_names, self.__database_api_identifier,
                                         self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.log_info("Account id:{}".format(account_id))
        operation = self.echo_ops.get_asset_issue_operation(echo=self.echo, issuer=self.echo_acc0,
                                                            value_amount=asset_value, value_asset_id=asset_id,
                                                            issue_to_account=account_id)

        lcc.set_step("Broadcast asset issue operation")
        self.broadcast_transaction(operation)

        lcc.set_step("Get account balances")
        response_id = self.send_request(self.get_request("get_account_balances", [account_id, [asset_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        lcc.set_step("Check that account: {} get assets".format(account_id))
        check_that("amount", response["amount"], equal_to(asset_value))

# todo: add operations "asset_reserve", "asset_fund_fee_pool", "asset_settle", "asset_global_settle", "asset_publish_feed", "proposal_create", "proposal_update", "proposal_delete", "withdraw_permission_create", "withdraw_permission_update", "withdraw_permission_claim", "withdraw_permission_delete",

    @lcc.prop("type", "method")
    @lcc.test("Check method broadcast_transaction with committee_member_create_operation")
    @lcc.depends_on("NetworkBroadcastApi.BroadcastTransaction.BroadcastTransaction.method_main_check")
    def broadcast_committee_member_create_operation(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        account_id = self.get_account_id(account_name, self.__database_api_identifier,
                                         self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(account_id))

        lcc.set_step("Add balance to pay fee for 'get_account_upgrade_operation' and update account to lifetime member")
        operation = self.echo_ops.get_account_upgrade_operation(self.echo, account_to_upgrade=account_id,
                                                                upgrade_to_lifetime_member=True)
        self.utils.add_balance_for_operations(self, account_id, operation, self.__database_api_identifier,
                                              log_broadcast=True)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get eth address")
        self.utils.perform_generate_eth_address_operation(self, account_id, self.__database_api_identifier)
        eth_account_address = self.utils.get_eth_address(self, account_id,
                                                         self.__database_api_identifier)["result"]["eth_addr"]

        lcc.set_step("Add balance to pay fee for 'get_committee_member_create_operation'")
        operation = self.echo_ops.get_committee_member_create_operation(echo=self.echo,
                                                                        committee_member_account=account_id,
                                                                        eth_address=eth_account_address,
                                                                        url="test_url")
        self.utils.add_balance_for_operations(self, account_id, operation, self.__database_api_identifier,
                                              log_broadcast=False)

        lcc.set_step("Broadcast committee member create operation")
        self.broadcast_transaction(operation)

        lcc.set_step("Check that account has become committee member")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", [account_name, 1]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0][0]
        check_that("account_name", account_name, equal_to(response))

# todo: add operations "committee_member_update", "committee_member_update_global_parameters", "vesting_balance_create",

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

        lcc.set_step("Add created assets to account")
        self.utils.add_assets_to_account(self, new_asset_amount, new_asset, self.echo_acc0,
                                         self.__database_api_identifier)

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform vesting balance create operation")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=new_account, amount=new_asset_amount,
                                                                       amount_asset_id=new_asset)

        lcc.set_step("Broadcast vesting balance create operation")
        self.broadcast_transaction(operation)

        lcc.set_step("Get created vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balances = self.get_response(response_id)["result"][0]
        lcc.set_step("Check that vesting balance equal to asset amount")
        check_that("id", vesting_balances["balance"]["amount"], equal_to(new_asset_amount))

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

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform vesting balance create operation and store vesting balance id")
        datetime = self.get_datetime(global_datetime=True)
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
        self.set_timeout_wait(10)
        operation = self.echo_ops.get_vesting_balance_withdraw_operation(echo=self.echo,
                                                                         vesting_balance=vesting_balance_id,
                                                                         owner=new_account, amount=asset_amount,
                                                                         amount_asset_id=new_asset)

        self.utils.add_balance_for_operations(self, new_account, operation, self.__database_api_identifier,
                                              log_broadcast=False)
        self.broadcast_transaction(operation)
