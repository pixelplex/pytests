# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_, is_integer,\
    equal_to, require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_vesting_balances'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_vesting_balances")
@lcc.suite("Check work of method 'get_vesting_balances'", rank=1)
class GetVestingBalances(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_vesting_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform vesting balance create operation")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=self.echo_acc0, amount=value_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))

        lcc.set_step("Get vesting balance of account and store last vesting balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [self.echo_acc0]),
                                        self.__database_api_identifier)

        result = self.get_response(response_id, log_response=True)["result"][-1]
        lcc.log_info("Call method 'get_vesting_balances' with param: '{}'".format(self.echo_acc0))

        lcc.set_step("Check simple work of method 'get_vesting_balances'")
        with this_dict(result):
            if check_that("balance_object", result, has_length(4)):
                if not self.validator.is_vesting_balance_id(result["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
                else:
                    lcc.log_info("'id' has correct format: vesting_balance_object_type")
                check_that_entry("id", is_(vesting_balance_id), quiet=True)
                check_that_entry("owner", is_(self.echo_acc0), quiet=True)
                balance = result["balance"]
                with this_dict(balance):
                    if check_that("balance", balance, has_length(2)):
                        self.check_uint256_numbers(balance, "amount", quiet=True)
                        check_that_entry("amount", is_(value_amount), quiet=True)
                        if not self.validator.is_asset_id(balance["asset_id"]):
                            lcc.log_error("Wrong format of 'asset_id', got: {}".format(result["asset_id"]))
                        else:
                            lcc.log_info("'asset_id' has correct format: asset_object_type")
                policy = result["policy"]
                with this_dict(policy):
                    if check_that("policy", policy, has_length(2)):
                        first_element = policy[0]
                        second_element = policy[1]
                        check_that("first element", first_element, is_(0), quiet=True)
                        with this_dict(second_element):
                            if not self.validator.is_iso8601(second_element["begin_timestamp"]):
                                lcc.log_error(
                                    "Wrong format of 'begin_timestamp', got: {}".format(
                                        second_element["begin_timestamp"]))
                            else:
                                lcc.log_info("'begin_timestamp' has correct format: iso8601")
                            check_that_entry("vesting_cliff_seconds", is_integer(), quiet=True)
                            check_that_entry("vesting_duration_seconds", is_integer(), quiet=True)
                            self.check_uint256_numbers(second_element, "begin_balance", quiet=True)
                            check_that_entry("begin_balance", is_(value_amount), quiet=True)


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_vesting_balances")
@lcc.suite("Positive testing of method 'get_vesting_balances'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    @staticmethod
    def get_random_amount(_to, _from=0):
        return round(random.uniform(_from, _to))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Work of method 'get_vesting_balances' with new account. In and withdraw balance")
    @lcc.depends_on("DatabaseApi.GetVestingBalances.GetVestingBalances.method_main_check")
    def in_and_out_vesting_balance_of_new_account(self, get_random_valid_account_name, get_random_integer):
        new_account = get_random_valid_account_name
        value_amount = get_random_integer

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform vesting balance create operation. Owner = new account")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=new_account, amount=value_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))

        lcc.set_step("Get vesting balance of created account and store last vesting balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][-1]
        lcc.log_info("Call method 'get_vesting_balances' with param: '{}'".format(new_account))

        lcc.set_step("Check that 'get_vesting_balances' method return broadcast operation")
        operation_data = operation[1]
        with this_dict(result):
            check_that_entry("id", is_(vesting_balance_id))
            check_that_entry("owner", is_(new_account))
            with this_dict(result["balance"]):
                check_that_entry("amount", is_(operation_data["amount"]["amount"]))
                check_that_entry("asset_id", is_(operation_data["amount"]["asset_id"]))
            with this_dict(result["policy"]):
                first_element = result["policy"][0]
                second_element = result["policy"][1]
                check_that("first element", first_element, is_(operation_data["policy"][0]))
                with this_dict(second_element):
                    check_that_entry("begin_timestamp", is_(operation_data["policy"][1]["begin_timestamp"]))
                    check_that_entry("vesting_cliff_seconds",
                                     is_(operation_data["policy"][1]["vesting_cliff_seconds"]))
                    check_that_entry("vesting_duration_seconds",
                                     is_(operation_data["policy"][1]["vesting_duration_seconds"]))
                    check_that_entry("begin_balance", is_(operation_data["amount"]["amount"]))

        lcc.set_step("Perform vesting balance withdraw operation. Owner = new account")
        withdraw_amount_1 = self.get_random_amount(value_amount)
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account,
                                                              withdraw_amount_1,
                                                              self.__database_api_identifier)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account,
                                                                                      withdraw_amount_1))

        lcc.set_step("Get vesting balance of created account after first withdraw")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balance = self.get_response(response_id)["result"][-1]
        balance_amount = vesting_balance["balance"]["amount"]
        begin_balance = vesting_balance["policy"][1]["begin_balance"]
        lcc.log_info("Call method 'get_vesting_balances' with param: '{}'".format(new_account))

        lcc.set_step("Check balance amount in 'get_vesting_balances' method after first withdraw")
        check_that("'balance_amount'", balance_amount, is_(value_amount - withdraw_amount_1))
        check_that("'begin_balance'", begin_balance, is_(value_amount))

        lcc.set_step("Perform vesting balance withdraw operation. Owner = new account. Withdraw all amount")
        withdraw_amount_2 = value_amount - withdraw_amount_1
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account,
                                                              withdraw_amount_2,
                                                              self.__database_api_identifier)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account,
                                                                                      withdraw_amount_2))

        lcc.set_step("Get vesting balance of created account after second withdraw")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balance = self.get_response(response_id)["result"][-1]
        balance_amount = vesting_balance["balance"]["amount"]
        begin_balance = vesting_balance["policy"][1]["begin_balance"]
        lcc.log_info("Call method 'get_vesting_balances' with param: '{}'".format(new_account))

        lcc.set_step("Check balance amount in 'get_vesting_balances' method after second withdraw")
        check_that("'balance_amount'", balance_amount, is_(0))
        check_that("'begin_balance'", begin_balance, is_(value_amount))

# todo: need add checks for changing 'asset_id', '0', 'begin_timestamp', 'vesting_cliff_seconds',
#  'vesting_duration_seconds'
    @lcc.prop("type", "method")
    @lcc.test("Work of method 'get_vesting_balances' with new owner and asset")
    @lcc.depends_on("DatabaseApi.GetVestingBalances.GetVestingBalances.method_main_check")
    def create_asset_and_get_vesting_balance_for_new_account(self, get_random_valid_asset_name, get_random_integer,
                                                             get_random_valid_account_name):
        value_amount = get_random_integer
        asset_name = get_random_valid_asset_name
        lcc.set_step("Create asset and get new asset id")
        asset_id = self.utils.get_asset_id(self, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(asset_id))
        lcc.set_step("Get asset issue")

        self.utils.add_assets_to_account(self, value_amount, asset_id, self.echo_acc0, self.__database_api_identifier)

        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc0, [asset_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        require_that("asset_id", response["asset_id"], equal_to(asset_id))
        require_that("amount", response["amount"], equal_to(value_amount))

        lcc.set_step("Create account")
        account = get_random_valid_account_name
        account_id = self.get_account_id(account, self.__database_api_identifier,
                                         self.__registration_api_identifier)
        lcc.log_info("New account is: {}, id of new account: {}".format(account, account_id))

        lcc.set_step("Get vesting balance with new owner: {}".format(account_id))

        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=account_id, amount=value_amount,
                                                                       amount_asset_id=asset_id)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                log_broadcast=False)

        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc0, [asset_id]]),
                                        self.__database_api_identifier)

        response = self.get_response(response_id)["result"][0]
        require_that("asset_id", response["asset_id"], equal_to(asset_id))
        require_that("amount", response["amount"], equal_to(0))

        lcc.set_step("Get vesting balance for account: {}".format(account_id))
        response_id = self.send_request(self.get_request("get_vesting_balances", [account_id]),
                                        self.__database_api_identifier)
        vesting_balance = self.get_response(response_id)["result"][0]
        with this_dict(vesting_balance):
            check_that("owner", vesting_balance["owner"], equal_to(account_id))
            check_that("amount", vesting_balance["balance"]["amount"], equal_to(value_amount))
            check_that("asset_id", vesting_balance["balance"]["asset_id"], equal_to(asset_id))
