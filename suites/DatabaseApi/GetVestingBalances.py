# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_, is_integer, \
    equal_to, require_that, require_that_entry, greater_than, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_vesting_balances'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_vesting_balances")
@lcc.suite("Check work of method 'get_vesting_balances'", rank=1)
class GetVestingBalances(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_vesting_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer

        lcc.set_step("Perform vesting balance create operation")
        broadcast_result = self.utils.perform_vesting_balance_create_operation(self, self.echo_acc0,
                                                                               self.echo_acc0, value_amount,
                                                                               self.__database_api_identifier)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(vesting_balance_id))

        lcc.set_step("Get vesting balance of account and store last vesting balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [self.echo_acc0]),
                                        self.__database_api_identifier)

        result = self.get_response(response_id)["result"][-1]
        lcc.log_info("Call method 'get_vesting_balances' with param: '{}'".format(self.echo_acc0))

        lcc.set_step("Check simple work of method 'get_vesting_balances'")
        with this_dict(result):
            if check_that("balance_object", result, has_length(5)):
                if not self.validator.is_vesting_balance_id(result["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
                else:
                    lcc.log_info("'id' has correct format: vesting_balance_object_type")
                check_that_entry("id", is_(vesting_balance_id), quiet=True)
                check_that_entry("owner", is_(self.echo_acc0), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)
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
                        # todo: first_element='0' - come from bitshares. Remove when corrected in Echo
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


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_vesting_balances")
@lcc.suite("Positive testing of method 'get_vesting_balances'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def get_random_amount(_to, _from=0):
        return round(random.uniform(_from, _to))

    @staticmethod
    def get_random_time_in_seconds(_from, _to):
        return random.randint(_from, _to)

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
                # todo: first_element='0' - come from bitshares. Remove when corrected in Echo
                check_that("first element", first_element, is_(operation_data["policy"][0]))
                with this_dict(second_element):
                    check_that_entry("begin_timestamp", is_(operation_data["policy"][1]["begin_timestamp"]))
                    check_that_entry("vesting_cliff_seconds", is_(operation_data["policy"][1]["vesting_cliff_seconds"]))
                    check_that_entry("vesting_duration_seconds",
                                     is_(operation_data["policy"][1]["vesting_duration_seconds"]))
                    check_that_entry("begin_balance", is_(operation_data["amount"]["amount"]))

        lcc.set_step("Perform vesting balance withdraw operation. Owner = new account")
        withdraw_amount_1 = self.get_random_amount(value_amount)
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, withdraw_amount_1,
                                                              self.__database_api_identifier)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account, withdraw_amount_1))

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
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, withdraw_amount_2,
                                                              self.__database_api_identifier)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account, withdraw_amount_2))

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

    @lcc.prop("type", "method")
    @lcc.test("Work of method 'get_vesting_balances' with created asset and echo asset")
    @lcc.depends_on("DatabaseApi.GetVestingBalances.GetVestingBalances.method_main_check")
    def create_vesting_balances_with_several_assets(self, get_random_valid_asset_name, get_random_integer,
                                                    get_random_valid_account_name, get_random_integer_up_to_fifty):
        new_asset_amount = get_random_integer
        echo_asset_amount = get_random_integer_up_to_fifty
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name
        list_operations = []

        lcc.set_step("Create asset and get new asset id")
        new_asset = self.utils.get_asset_id(self, new_asset, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset))

        lcc.set_step("Add created assets to account")
        self.utils.add_assets_to_account(self, new_asset_amount, new_asset, self.echo_acc0,
                                         self.__database_api_identifier)
        lcc.log_info("Created '{}' assets added to '{}' account successfully".format(new_asset, self.echo_acc0))

        lcc.set_step("Check that new assets are displayed on the account balance")
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc0, [new_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        with this_dict(response):
            require_that_entry("asset_id", equal_to(new_asset))
            require_that_entry("amount", equal_to(new_asset_amount))

        lcc.set_step("Check that account have enough echo assets")
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc0, [self.echo_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]
        require_that("balance asset_id", response["asset_id"], equal_to(self.echo_asset))
        require_that("balance asset amount", int(response["amount"]), greater_than(new_asset_amount))

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform vesting balance create operation. Owner = new account")
        assets = [self.echo_asset, new_asset]
        amounts = [echo_asset_amount, new_asset_amount]
        for i in range(len(assets)):
            operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                           owner=new_account, amount=amounts[i],
                                                                           amount_asset_id=assets[i])
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            list_operations.append(collected_operation)
        self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations)

        lcc.set_step("Get created vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balances = self.get_response(response_id)["result"]
        for i in range(len(vesting_balances)):
            with this_dict(vesting_balances[i]):
                check_that_entry("owner", equal_to(new_account))
                with this_dict(vesting_balances[i]["balance"]):
                    check_that_entry("amount", equal_to(amounts[i]))
                    check_that_entry("asset_id", equal_to(assets[i]))

    @lcc.prop("type", "method")
    @lcc.test("Modified begin_timestamp and try to withdraw vesting balance")
    @lcc.depends_on("DatabaseApi.GetVestingBalances.GetVestingBalances.method_main_check")
    def create_vesting_balance_with_begin_timestamp_in_future(self, get_random_valid_asset_name, get_random_integer,
                                                              get_random_valid_account_name):
        asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name
        added_seconds = 30

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
        datetime = self.utils.set_datetime_variable(self.get_datetime(global_datetime=True), seconds=added_seconds)
        lcc.log_info("Set begin_timestamp variable: '{}'".format(datetime))
        broadcast_result = self.utils.perform_vesting_balance_create_operation(self, self.echo_acc0,
                                                                               new_account, asset_amount,
                                                                               self.__database_api_identifier,
                                                                               amount_asset_id=new_asset,
                                                                               begin_timestamp=datetime)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created, begin_timestamp='{}'".format(vesting_balance_id, datetime))

        lcc.set_step("Get created vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balance_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("vesting balance amount", vesting_balance_amount, equal_to(asset_amount))

        lcc.set_step("Try to withdraw balance when begin_timestamp is not begin")
        try:
            self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, asset_amount,
                                                                  self.__database_api_identifier,
                                                                  amount_asset_id=new_asset)
            lcc.log_error("Error: broadcast transaction complete when begin_timestamp is not begin")
        except RPCError as e:
            lcc.log_info(str(e))

        lcc.set_step("Wait for begin timestamp")
        self.set_timeout_wait(seconds=added_seconds)

        lcc.set_step("Withdraw balance after beginning timestamp")
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, asset_amount,
                                                              self.__database_api_identifier,
                                                              amount_asset_id=new_asset)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account, asset_amount))

        lcc.set_step("Get updated vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        updated_vesting_balance_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("updated vesting balance amount", updated_vesting_balance_amount,
                   equal_to(vesting_balance_amount - asset_amount))

    @lcc.prop("type", "method")
    @lcc.test("Modified vesting_cliff_seconds and try to withdraw vesting balance")
    @lcc.tags("qqq")
    # @lcc.depends_on("DatabaseApi.GetVestingBalances.GetVestingBalances.method_main_check")
    def create_vesting_balance_with_vesting_cliff_seconds(self, get_random_valid_asset_name, get_random_integer,
                                                          get_random_valid_account_name):
        asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name
        vesting_cliff_seconds = 30

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
        broadcast_result = self.utils.perform_vesting_balance_create_operation(self, self.echo_acc0,
                                                                               new_account, asset_amount,
                                                                               self.__database_api_identifier,
                                                                               amount_asset_id=new_asset,
                                                                               begin_timestamp=datetime,
                                                                               cliff_seconds=vesting_cliff_seconds)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info(
            "Vesting balance object '{}' created, vesting_cliff_seconds='{}'".format(vesting_balance_id,
                                                                                     vesting_cliff_seconds))

        lcc.set_step("Get created vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balance_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("vesting balance amount", vesting_balance_amount, equal_to(asset_amount))

        lcc.set_step("Try to withdraw balance when vesting_cliff_seconds not finished")
        try:
            self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, asset_amount,
                                                                  self.__database_api_identifier,
                                                                  amount_asset_id=new_asset)
            lcc.log_error("Error: broadcast transaction complete when vesting_cliff_seconds is not finished")
        except RPCError as e:
            lcc.log_info(str(e))

        lcc.set_step("Wait for finish vesting_cliff_seconds")
        self.set_timeout_wait(seconds=vesting_cliff_seconds)

        lcc.set_step("Withdraw balance after finish vesting_cliff_seconds")
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, asset_amount,
                                                              self.__database_api_identifier,
                                                              amount_asset_id=new_asset)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account, asset_amount))

        lcc.set_step("Get updated vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        updated_vesting_balance_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("updated vesting balance amount", updated_vesting_balance_amount,
                   equal_to(vesting_balance_amount - asset_amount))

    @lcc.prop("type", "method")
    @lcc.test("Modified vesting_duration_seconds and try to withdraw vesting balance")
    @lcc.depends_on("DatabaseApi.GetVestingBalances.GetVestingBalances.method_main_check")
    def create_vesting_balance_with_vesting_duration_seconds(self, get_random_valid_asset_name, get_random_integer,
                                                             get_random_valid_account_name):
        asset_amount = get_random_integer
        new_asset = get_random_valid_asset_name
        new_account = get_random_valid_account_name
        duration_seconds = 60
        part = 3

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
        broadcast_result = self.utils.perform_vesting_balance_create_operation(self, self.echo_acc0,
                                                                               new_account, asset_amount,
                                                                               self.__database_api_identifier,
                                                                               amount_asset_id=new_asset,
                                                                               begin_timestamp=datetime,
                                                                               duration_seconds=duration_seconds)
        vesting_balance_id = self.get_operation_results_ids(broadcast_result)
        lcc.log_info(
            "Vesting balance object '{}' created, vesting_duration_seconds='{}'".format(vesting_balance_id,
                                                                                        duration_seconds))

        lcc.set_step("Get created vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        vesting_balance_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("vesting balance amount", vesting_balance_amount, equal_to(asset_amount))

        lcc.set_step("Try to withdraw all balance when vesting_duration_seconds not finished")
        try:
            self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, asset_amount,
                                                                  self.__database_api_identifier,
                                                                  amount_asset_id=new_asset)
            lcc.log_error("Error: broadcast transaction complete when vesting_duration_seconds is not finish")
        except RPCError as e:
            lcc.log_info(str(e))

        lcc.set_step("Wait when 1/{} part of vesting_duration_seconds finish".format(part))
        self.set_timeout_wait(seconds=duration_seconds // part)

        lcc.set_step("Withdraw balance after finish vesting_cliff_seconds")
        withdraw_amount = asset_amount // part
        self.utils.perform_vesting_balance_withdraw_operation(self, vesting_balance_id, new_account, withdraw_amount,
                                                              self.__database_api_identifier,
                                                              amount_asset_id=new_asset)
        lcc.log_info("Withdraw vesting balance from '{}' account, amount='{}'".format(new_account, withdraw_amount))

        lcc.set_step("Get updated vesting account balance")
        response_id = self.send_request(self.get_request("get_vesting_balances", [new_account]),
                                        self.__database_api_identifier)
        updated_vesting_balance_amount = self.get_response(response_id)["result"][0]["balance"]["amount"]
        check_that("updated vesting balance amount", updated_vesting_balance_amount,
                   equal_to(vesting_balance_amount - withdraw_amount))
