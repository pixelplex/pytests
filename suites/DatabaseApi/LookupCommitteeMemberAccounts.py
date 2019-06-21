# -*- coding: utf-8 -*-
import json

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length

from common.base_test import BaseTest
from project import GENESIS

SUITE = {
    "description": "Method 'lookup_committee_member_accounts'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "lookup_committee_member_accounts")
@lcc.suite("Check work of method 'lookup_committee_member_accounts'", rank=1)
class LookupCommitteeMemberAccounts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'lookup_committee_member_accounts'")
    def method_main_check(self):
        # todo: remove 'json.load(open())' when added 0.7 changes
        initial_committee_members = json.load(open(GENESIS))["initial_committee_candidates"]
        initial_committee_members_names = []

        lcc.set_step("Get info about default committee members")
        for i in range(len(initial_committee_members)):
            initial_committee_members_names.append(initial_committee_members[i]["owner_name"])
        limit = len(initial_committee_members_names)
        params = [initial_committee_members_names[0], limit]
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call method 'get_committee_members' with params: {}".format(params))

        lcc.set_step("Check length of received committee members")
        require_that("'list of received committee members'", response["result"], has_length(limit))

        for i in range(len(response["result"])):
            lcc.set_step("Checking committee member #{}".format(i))
            committee_member = response["result"][i]
            if not self.validator.is_account_name(committee_member[0]):
                lcc.log_error("Wrong format of first element, need='name', got: {}".format(committee_member[0]))
            else:
                lcc.log_info("First element has correct format: account name")
            if not self.validator.is_committee_member_id(committee_member[1]):
                lcc.log_error(
                    "Wrong format of second element, need='committee_member_id', got: {}".format(committee_member[1]))
            else:
                lcc.log_info("Second element has correct format: committee_member_object_type")
