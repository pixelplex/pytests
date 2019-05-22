# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_integer, is_str, is_dict, \
    is_list, require_that, is_, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_accounts'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_accounts")
@lcc.suite("Check work of method 'get_accounts'", rank=1)
class GetAccounts(BaseTest):

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
    @lcc.test("Simple work of method 'get_accounts'")
    def method_main_check(self):
        lcc.set_step("Get info about default accounts")
        params = ["1.2.0", "1.2.1"]
        response_id = self.send_request(self.get_request("get_accounts", [params]), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_accounts' with params: {}".format(params))

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


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_accounts")
@lcc.suite("Positive testing of method 'get_accounts'", rank=2)
class PositiveTesting(BaseTest):

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
    @lcc.test("Create accounts using account_create operation and get info about them")
    @lcc.depends_on("DatabaseApi.GetAccounts.GetAccounts.method_main_check")
    def get_info_about_created_accounts(self, get_random_valid_account_name):
        accounts = [get_random_valid_account_name + "0", get_random_valid_account_name + "1"]
        public_data_accounts = [self.generate_keys(), self.generate_keys()]

        lcc.set_step("Perform two account creation operations and store accounts ids")
        accounts = self.utils.get_account_id(self, self.echo, accounts, public_data_accounts,
                                             self.__database_api_identifier, need_operations=True)
        lcc.log_info("Two accounts created, ids: 1='{}', 2='{}'".format(accounts.get("accounts_ids")[0],
                                                                        accounts.get("accounts_ids")[1]))

        lcc.set_step("Get a list of created accounts by ID")
        response_id = self.send_request(self.get_request("get_accounts", [accounts.get("accounts_ids")]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_accounts' with params: {}".format(accounts.get("accounts_ids")))

        for i in range(len(response["result"])):
            lcc.set_step("Checking account #{}".format(i))
            performed_operations = accounts.get("list_operations")[i][0][1]
            account_info = response["result"][i]
            with this_dict(account_info):
                check_that_entry("registrar", equal_to(performed_operations["registrar"]))
                check_that_entry("referrer", equal_to(performed_operations["referrer"]))
                check_that_entry("referrer_rewards_percentage", equal_to(performed_operations["referrer_percent"]))
                check_that_entry("name", equal_to(performed_operations["name"]))
                check_that_entry("active", equal_to(performed_operations["active"]))
                check_that_entry("ed_key", equal_to(performed_operations["ed_key"]))
                check_that_entry("options", equal_to(performed_operations["options"]))
