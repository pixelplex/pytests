# -*- coding: utf-8 -*-
import json

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_str

from common.base_test import BaseTest
from project import GENESIS

SUITE = {
    "description": "Method 'lookup_vote_ids'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "lookup_vote_ids")
@lcc.suite("Check work of method 'lookup_vote_ids'", rank=1)
class LookupVoteIds(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'lookup_vote_ids'")
    def method_main_check(self):
        # todo: remove 'json.load(open())' when added 0.7 changes
        initial_committee_members = json.load(open(GENESIS))["initial_committee_candidates"]
        initial_committee_members_vote_ids = []

        lcc.set_step("Store vote_ids of initial committee members")
        for i in range(len(initial_committee_members)):
            initial_committee_members_vote_ids.append("0:{}".format(str(i)))
        lcc.log_info("Initial committee members vote_ids: '{}'".format(initial_committee_members_vote_ids))

        lcc.set_step("Get info about default committee_account using vote_id")
        params = initial_committee_members_vote_ids
        response_id = self.send_request(self.get_request("lookup_vote_ids", [params]), self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call method 'lookup_vote_ids' with params: {}".format(params))

        initial_committee_info = response["result"]
        for i in range(len(initial_committee_info)):
            lcc.set_step(
                "Check initial committee member #{} using account_id '{}'".format(i, params[i]))
            with this_dict(initial_committee_info[i]):
                if check_that("committee_member_info", initial_committee_info, has_length(6)):
                    if not self.validator.is_committee_member_id(initial_committee_info[i]["id"]):
                        lcc.log_error("Wrong format of 'id', got: {}".format(
                            initial_committee_info[i]["id"]))
                    else:
                        lcc.log_info("'id' has correct format: committee_member_object_type")
                    if not self.validator.is_account_id(initial_committee_info[i]["committee_member_account"]):
                        lcc.log_error("Wrong format of 'committee_member_account', got: {}".format(
                            initial_committee_info[i]["committee_member_account"]))
                    else:
                        lcc.log_info("'committee_member_account' has correct format: account_object_type")
                    check_that_entry("vote_id", is_str(params[i]), quiet=True)
                    self.check_uint256_numbers(response["result"][i], "total_votes", quiet=True)
                    check_that_entry("url", is_str(), quiet=True)
                    # todo: delete replace Bug ECHO-961
                    if not self.validator.is_eth_address(
                            initial_committee_info[i]["eth_address"].replace("0000000000000000000000000000000000000000",
                                                                             "")):
                        lcc.log_error("Wrong format of 'eth_address', got: {}".format(
                            initial_committee_info[i]["eth_address"].replace("0000000000000000000000000000000000000000",
                                                                             "")))
                    else:
                        lcc.log_info("'eth_address' has correct format: eth_address_type")
