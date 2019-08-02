# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_integer, is_str, is_dict, \
    is_list, require_that, is_, equal_to, is_bool

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_full_accounts'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_full_accounts")
@lcc.suite("Check work of method 'get_full_accounts'", rank=1)
class GetFullAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def check_fields_account_ids_format(self, response, field):
        if not self.validator.is_account_id(response[field]):
            lcc.log_error("Wrong format of '{}', got: {}".format(field, response[field]))
        else:
            lcc.log_info("'{}' has correct format: account_object_type".format(field))

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_full_accounts'")
    def method_main_check(self):
        lcc.set_step("Get full info about default accounts")
        params = ["1.2.0", "1.2.1"]
        response_id = self.send_request(self.get_request("get_full_accounts", [params, False]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_full_accounts' with params: {}".format(params))

        lcc.set_step("Check length of received accounts")
        require_that(
            "'list of received accounts'",
            len(response["result"]), is_(len(params))
        )

        for i in range(len(response["result"])):
            lcc.set_step("Checking account #{} - '{}'".format(i, params[i]))
            check_that("account_id", response["result"][i][0], equal_to(params[i]))
            full_account_info = response["result"][i][1]
            if check_that("full_account_info", full_account_info, has_length(14)):
                account_info = full_account_info.get("account")
                with this_dict(account_info):
                    if check_that("account_info", account_info, has_length(20)):
                        check_that_entry("id", is_str(params[i]))
                        if not self.validator.is_iso8601(account_info["membership_expiration_date"]):
                            lcc.log_error("Wrong format of 'membership_expiration_date', got: {}".format(
                                account_info["membership_expiration_date"]))
                        else:
                            lcc.log_info("'membership_expiration_date' has correct format: iso8601")
                        account_ids_format = ["registrar", "referrer", "lifetime_referrer"]
                        for j in range(len(account_ids_format)):
                            self.check_fields_account_ids_format(account_info, account_ids_format[j])
                        check_that_entry("network_fee_percentage", is_integer(), quiet=True)
                        check_that_entry("lifetime_referrer_fee_percentage", is_integer(), quiet=True)
                        check_that_entry("referrer_rewards_percentage", is_integer(), quiet=True)
                        if not self.validator.is_account_name(account_info["name"]):
                            lcc.log_error("Wrong format of 'name', got: {}".format(account_info["name"]))
                        else:
                            lcc.log_info("'name' has correct format: account_name")
                        check_that_entry("active", is_dict(), quiet=True)
                        if not self.validator.is_echorand_key(account_info["echorand_key"]):
                            lcc.log_error(
                                "Wrong format of 'echorand_key', got: {}".format(account_info["echorand_key"]))
                        else:
                            lcc.log_info("'echorand_key' has correct format: echo_rand_key")
                        check_that_entry("options", is_dict(), quiet=True)
                        if not self.validator.is_account_statistics_id(account_info["statistics"]):
                            lcc.log_error("Wrong format of 'statistics', got: {}".format(account_info["statistics"]))
                        else:
                            lcc.log_info("'statistics' has correct format: account_statistics_object_type")
                        check_that_entry("whitelisting_accounts", is_list(), quiet=True)
                        check_that_entry("blacklisting_accounts", is_list(), quiet=True)
                        check_that_entry("whitelisted_accounts", is_list(), quiet=True)
                        check_that_entry("blacklisted_accounts", is_list(), quiet=True)
                        check_that_entry("active_special_authority", is_list(), quiet=True)
                        check_that_entry("top_n_control_flags", is_integer(), quiet=True)
                        check_that_entry("extensions", is_list(), quiet=True)

                        lcc.set_step("Check 'active' field")
                        with this_dict(account_info["active"]):
                            if check_that("active", account_info["active"], has_length(3)):
                                check_that_entry("weight_threshold", is_integer(), quiet=True)
                                check_that_entry("account_auths", is_list(), quiet=True)
                                check_that_entry("key_auths", is_list(), quiet=True)

                        lcc.set_step("Check 'options' field")
                        with this_dict(account_info["options"]):
                            if check_that("active", account_info["options"], has_length(5)):
                                account_ids_format = ["voting_account", "delegating_account"]
                                for k in range(len(account_ids_format)):
                                    self.check_fields_account_ids_format(account_info["options"], account_ids_format[k])
                                check_that_entry("num_committee", is_integer(), quiet=True)
                                check_that_entry("votes", is_list(), quiet=True)
                                check_that_entry("extensions", is_list(), quiet=True)

                lcc.set_step("Check 'statistics' field")
                account_statistics = full_account_info.get("statistics")
                with this_dict(account_statistics):
                    if check_that("account_statistics", account_statistics, has_length(13)):
                        if not self.validator.is_account_statistics_id(account_statistics["id"]):
                            lcc.log_error("Wrong format of 'id', got: {}".format(account_statistics["id"]))
                        else:
                            lcc.log_info("'id' has correct format: account_statistics_object_type")
                        check_that_entry("owner", is_str(params[i]))
                        if not self.validator.is_account_transaction_history_id(account_statistics["most_recent_op"]):
                            lcc.log_error("Wrong format of 'most_recent_op', got: {}".format(
                                account_statistics["most_recent_op"]))
                        else:
                            lcc.log_info("'most_recent_op' has correct format: account_transaction_history_object_type")
                        check_that_entry("total_ops", is_integer(), quiet=True)
                        check_that_entry("removed_ops", is_integer(), quiet=True)
                        check_that_entry("total_blocks", is_integer(), quiet=True)
                        check_that_entry("total_core_in_orders", is_integer(), quiet=True)
                        check_that_entry("lifetime_fees_paid", is_integer(), quiet=True)
                        check_that_entry("pending_fees", is_integer(), quiet=True)
                        check_that_entry("pending_vested_fees", is_integer(), quiet=True)
                        check_that_entry("generated_eth_address", is_bool(), quiet=True)
                        check_that_entry("committeeman_rating", is_integer(), quiet=True)
                        check_that_entry("extensions", is_list(), quiet=True)

                with this_dict(full_account_info):
                    lcc.set_step("Check 'registrar_name', 'referrer_name', 'lifetime_referrer_name' fields")
                    if not self.validator.is_account_name(full_account_info["registrar_name"]):
                        lcc.log_error(
                            "Wrong format of 'registrar_name', got: {}".format(full_account_info["registrar_name"]))
                    else:
                        lcc.log_info("'registrar_name' has correct format: account_name")
                    if not self.validator.is_account_name(full_account_info["referrer_name"]):
                        lcc.log_error(
                            "Wrong format of 'referrer_name', got: {}".format(full_account_info["referrer_name"]))
                    else:
                        lcc.log_info("'referrer_name' has correct format: account_name")
                    if not self.validator.is_account_name(full_account_info["lifetime_referrer_name"]):
                        lcc.log_error("Wrong format of 'lifetime_referrer_name', got: {}".format(
                            full_account_info["lifetime_referrer_name"]))
                    else:
                        lcc.log_info("'lifetime_referrer_name' has correct format: account_name")
                    lcc.set_step("Check 'votes' field")
                    check_that_entry("votes", is_list(), quiet=True)
                    lcc.set_step("Check 'balances' field")
                    check_that_entry("balances", is_list(), quiet=True)
                    balance = full_account_info["balances"]
                    if balance:
                        for j in range(len(balance)):
                            lcc.set_step("Check 'balance #{}' field".format(str(j)))
                            if check_that("account_balances", balance[j], has_length(5)):
                                with this_dict(balance[j]):
                                    if not self.validator.is_account_balance_id(balance[j]["id"]):
                                        lcc.log_error(
                                            "Wrong format of 'id', got: {}".format(balance[j]["id"]))
                                    else:
                                        lcc.log_info("'id' has correct format: account_balance_object_type")
                                    self.check_fields_account_ids_format(balance[j], "owner")
                                    if not self.validator.is_asset_id(balance[j]["asset_type"]):
                                        lcc.log_error(
                                            "Wrong format of 'asset_type', got: {}".format(balance[j]["asset_type"]))
                                    else:
                                        lcc.log_info("'asset_type' has correct format: asset_object_type")
                                    check_that_entry("balance", is_integer(), quiet=True)
                                    check_that_entry("extensions", is_list(), quiet=True)
                    lcc.set_step("Check 'vesting_balances' field")
                    check_that_entry("vesting_balances", is_list(), quiet=True)
                    lcc.set_step("Check 'limit_orders' field")
                    check_that_entry("limit_orders", is_list(), quiet=True)
                    lcc.set_step("Check 'call_orders' field")
                    check_that_entry("call_orders", is_list(), quiet=True)
                    lcc.set_step("Check 'settle_orders' field")
                    check_that_entry("settle_orders", is_list(), quiet=True)
                    lcc.set_step("Check 'proposals' field")
                    check_that_entry("proposals", is_list(), quiet=True)
                    lcc.set_step("Check 'assets' field")
                    check_that_entry("assets", is_list(), quiet=True)
                    lcc.set_step("Check 'withdraws' field")
                    check_that_entry("withdraws", is_list(), quiet=True)
