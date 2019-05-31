# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_integer, is_dict, \
    is_list, require_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'lookup_account_names'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "lookup_account_names")
@lcc.suite("Check work of method 'lookup_account_names'", rank=1)
class LookupAccountNames(BaseTest):

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
    @lcc.test("Simple work of method 'lookup_account_names'")
    def method_main_check(self):
        lcc.set_step("Get info about default account")
        params = [self.echo_acc0, self.echo_acc1, self.echo_acc2]
        response_id = self.send_request(self.get_request("lookup_account_names", [params]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call method 'lookup_account_names' with param: {}".format(params))

        lcc.set_step("Check length of received accounts")
        require_that(
            "'list of received accounts'",
            len(response["result"]), is_(len(params))
        )

        for i in range(len(response["result"])):
            lcc.set_step("Checking account #{} - '{}'".format(i, params[i]))
            account_info = response["result"][i]
            with this_dict(account_info):
                if check_that("account_info", account_info, has_length(20)):
                    self.check_fields_account_ids_format(account_info, "id")
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
                    if not self.validator.is_echo_rand_key(account_info["ed_key"]):
                        lcc.log_error("Wrong format of 'ed_key', got: {}".format(account_info["ed_key"]))
                    else:
                        lcc.log_info("'ed_key' has correct format: echo_rand_key")
                    check_that_entry("options", is_dict(), quiet=True)
                    if not self.validator.is_account_statistics_id(account_info["statistics"]):
                        lcc.log_error("Wrong format of 'statistics', got: {}".format(account_info["statistics"]))
                    else:
                        lcc.log_info("'statistics' has correct format: account_statistics_object_type")
                    check_that_entry("whitelisting_accounts", is_list(), quiet=True)
                    check_that_entry("blacklisting_accounts", is_list(), quiet=True)
                    check_that_entry("whitelisted_accounts", is_list(), quiet=True)
                    check_that_entry("blacklisted_accounts", is_list(), quiet=True)
                    # todo: remove 'owner_special_authority'. Improve: "ECHO-829"
                    check_that_entry("owner_special_authority", is_list(), quiet=True)
                    check_that_entry("active_special_authority", is_list(), quiet=True)
                    check_that_entry("top_n_control_flags", is_integer(), quiet=True)

                    lcc.set_step("Check 'active' field")
                    with this_dict(account_info["active"]):
                        if check_that("active", account_info["active"], has_length(3)):
                            check_that_entry("weight_threshold", is_integer(), quiet=True)
                            check_that_entry("account_auths", is_list(), quiet=True)
                            check_that_entry("key_auths", is_list(), quiet=True)

                    lcc.set_step("Check 'options' field")
                    with this_dict(account_info["options"]):
                        if check_that("active", account_info["options"], has_length(6)):
                            if not self.validator.is_public_key(account_info["options"]["memo_key"]):
                                lcc.log_error(
                                    "Wrong format of 'memo_key', got: {}".format(account_info["options"]["memo_key"]))
                            else:
                                lcc.log_info("'memo_key' has correct format: public_key")
                            account_ids_format = ["voting_account", "delegating_account"]
                            for k in range(len(account_ids_format)):
                                self.check_fields_account_ids_format(account_info["options"], account_ids_format[k])
                            check_that_entry("num_committee", is_integer(), quiet=True)
                            check_that_entry("votes", is_list(), quiet=True)
                            check_that_entry("extensions", is_list(), quiet=True)
