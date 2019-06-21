# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, this_dict, check_that_entry, is_str, is_list, is_integer, \
    is_dict, equal_to, check_that, is_none, has_length, is_not_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'lookup_accounts'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "lookup_accounts")
@lcc.suite("Check work of method 'lookup_accounts'", rank=1)
class LookupAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.nathan_account_name = "nathan"

    def check_lookup_account_structure(self, lookup_account):
        if not self.validator.is_account_name(lookup_account[0]):
            lcc.log_error("Wrong format of 'account name', got: {}".format(lookup_account[0]))
        else:
            lcc.log_info("'account name' has correct format: account_name")

        if not self.validator.is_account_id(lookup_account[1]):
            lcc.log_error("Wrong format of 'account id', got: {}".format(lookup_account[1]))
        else:
            lcc.log_info("'account id' has correct format: account_id")

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'lookup_accounts'")
    def method_main_check(self):
        lcc.set_step("Lookup nathan account and check result structure")
        limit = 1
        response_id = self.send_request(self.get_request("lookup_accounts",
                                        [self.nathan_account_name, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_accounts' with lower_bound_name='{}',limit='{}' parameters".format(
            self.nathan_account_name, limit))

        lcc.set_step("Check simple work of method 'lookup_asset_symbols'")
        lookup_account = response["result"][0]

        require_that(
            "'result lookup account'",
            lookup_account, is_not_none()
        )

        require_that(
            "'lookup account",
            lookup_account, has_length(2)
        )

        self.check_lookup_account_structure(lookup_account)
