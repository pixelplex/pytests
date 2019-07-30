# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_integer, is_dict, \
    is_list, require_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'lookup_account_names'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
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

    def check_account_structure(self, account_info):
        with this_dict(account_info):
            if not (19 < len(account_info) < 22):
                raise Exception(
                    "Account object has wrong structure. Need len=[20, 21], got len={}, response: {}".format(
                        str(len(account_info)), str(account_info)))
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
            if not self.validator.is_echorand_key(account_info["echorand_key"]):
                lcc.log_error("Wrong format of 'echorand_key', got: {}".format(account_info["echorand_key"]))
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
            if len(account_info) == 21:
                if not self.validator.is_vesting_balance_id(account_info["cashback_vb"]):
                    lcc.log_error("Wrong format of 'cashback_vb', got: {}".format(account_info["cashback_vb"]))
                else:
                    lcc.log_info("'cashback_vb' has correct format: vesting_balance_object_type")
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

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'lookup_account_names'")
    def method_main_check(self):
        lcc.set_step("Get info about default account")
        params = [self.accounts[0], self.accounts[1], self.accounts[2]]
        response_id = self.send_request(self.get_request("lookup_account_names", [params]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_account_names' with param: {}".format(params))

        lcc.set_step("Check length of received accounts")
        require_that(
            "'list of received accounts'",
            response["result"], has_length(len(params))
        )

        for account_num, account_info in enumerate(response["result"]):
            lcc.set_step("Checking account #{} - '{}'".format(account_num, params[account_num]))
            self.check_account_structure(account_info)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "lookup_account_names")
@lcc.suite("Positive testing of method 'lookup_account_names'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def compare_accounts(account, performed_account, account_is_created=False):
        with this_dict(account):
            check_that_entry("registrar", equal_to(performed_account["registrar"]))
            check_that_entry("referrer", equal_to(performed_account["referrer"]))
            referrer_percent_field_name = "referrer_percent"
            if account_is_created:
                referrer_percent_field_name = "referrer_rewards_percentage"
            check_that_entry("referrer_rewards_percentage", equal_to(performed_account[referrer_percent_field_name]))
            check_that_entry("name", equal_to(performed_account["name"]))
            check_that_entry("active", equal_to(performed_account["active"]))
            check_that_entry("echorand_key", equal_to(performed_account["echorand_key"]))
            check_that_entry("options", equal_to(performed_account["options"]))

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
    @lcc.test("Create accounts using account_create operation and get info about them")
    @lcc.depends_on("DatabaseApi.LookupAccountNames.LookupAccountNames.method_main_check")
    def get_info_about_created_accounts(self, get_random_valid_account_name):
        accounts = ["{}{}".format(get_random_valid_account_name, num) for num in range(2)]
        accounts_public_keys = [self.generate_keys(), self.generate_keys()]

        lcc.set_step("Perform two account creation operations and store accounts ids")
        accounts = self.utils.get_account_id(self, accounts, accounts_public_keys, self.__database_api_identifier,
                                             need_operations=True)
        lcc.log_info("Two accounts created, ids: 1='{}', 2='{}'".format(accounts.get("accounts_ids")[0],
                                                                        accounts.get("accounts_ids")[1]))

        lcc.set_step("Get a list of created accounts by names")
        response_id = self.send_request(self.get_request("lookup_account_names", [accounts.get("account_names")]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_account_names' with params: {}".format(accounts.get("account_names")))

        accounts_info = response["result"]
        for account_num, account in enumerate(accounts_info):
            lcc.set_step("Checking account #{}".format(account_num))
            perform_operation = accounts.get("list_operations")[account_num][0][1]
            self.compare_accounts(account, perform_operation)

    @lcc.prop("type", "method")
    @lcc.test("Create account using account_create operation and "
              "compare response from 'lookup_account_names' and 'get_objects'")
    @lcc.depends_on("DatabaseApi.LookupAccountNames.LookupAccountNames.method_main_check")
    def compare_with_method_get_objects(self, get_random_valid_account_name):
        account_name = get_random_valid_account_name
        public_key = self.generate_keys()[1]

        lcc.set_step("Perform account creation operation")
        operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key, public_key,
                                                               registrar=self.echo_acc0, signer=self.echo_acc0)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Account is not created")
        operation_result = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Account is created, id='{}'".format(operation_result))

        lcc.set_step("Get account by name")
        response_id = self.send_request(self.get_request("lookup_account_names", [[account_name]]),
                                        self.__database_api_identifier)
        response_1 = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_by_name' with param: {}".format(account_name))

        lcc.set_step("Get account by id")
        account_id = self.get_account_by_name(account_name, self.__database_api_identifier).get("result").get("id")
        response_id = self.send_request(self.get_request("get_objects", [[account_id]]),
                                        self.__database_api_identifier)
        response_2 = self.get_response(response_id)
        lcc.log_info("Call method 'get_objects' with param: {}".format(account_id))

        lcc.set_step("Checking created account")
        account_info_1 = response_1["result"]
        account_info_2 = response_2["result"]
        for account_num in range(len(account_info_1)):
            self.compare_accounts(account_info_1[account_num], account_info_2[account_num],
                                  account_is_created=True)
