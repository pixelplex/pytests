# -*- coding: utf-8 -*-
import json

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_str

from common.base_test import BaseTest
from project import GENESIS

SUITE = {
    "description": "Method 'get_committee_member_by_account'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_committee_member_by_account")
@lcc.suite("Check work of method 'get_committee_member_by_account'", rank=1)
class GetCommitteeMemberByAccount(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_committee_member_by_account'")
    def method_main_check(self):
        # todo: remove 'json.load(open())' when added 0.7 changes
        initial_committee_candidates = json.load(open(GENESIS))["initial_committee_candidates"]
        initial_committee_candidates_names = []
        committee_members_account_ids = []

        lcc.set_step("Get info about default accounts and store their ids")
        for i in range(len(initial_committee_candidates)):
            initial_committee_candidates_names.append(initial_committee_candidates[i]["owner_name"])
            response_id = self.send_request(
                self.get_request("get_account_by_name", [initial_committee_candidates_names[i]]),
                self.__database_api_identifier)
            committee_members_account_ids.append(self.get_response(response_id)["result"]["id"])
        lcc.log_info("Initial committee account are stored: {}".format(committee_members_account_ids))

        lcc.set_step("Get info about default committee_account using account_id")
        for i in range(len(committee_members_account_ids)):
            response_id = self.send_request(
                self.get_request("get_committee_member_by_account", [committee_members_account_ids[i]]),
                self.__database_api_identifier)
            response = self.get_response(response_id, log_response=True)
            initial_committee_info = response["result"]
            lcc.set_step(
                "Check initial committee member #{} using account_id '{}'".format(i, committee_members_account_ids[i]))
            with this_dict(initial_committee_info):
                if check_that("committee_member_info", initial_committee_info, has_length(7)):
                    if not self.validator.is_committee_member_id(initial_committee_info["id"]):
                        lcc.log_error("Wrong format of 'id', got: {}".format(
                            initial_committee_info["id"]))
                    else:
                        lcc.log_info("'id' has correct format: committee_member_object_type")
                    check_that_entry("committee_member_account", is_str(committee_members_account_ids[i]), quiet=True)
                    if not self.validator.is_vesting_balance_id(initial_committee_info["pay_vb"]):
                        lcc.log_error("Wrong format of 'pay_vb', got: {}".format(
                            initial_committee_info["pay_vb"]))
                    else:
                        lcc.log_info("'pay_vb' has correct format: vesting_balance_object_type")
                    if not self.validator.is_vote_id(initial_committee_info["vote_id"]):
                        lcc.log_error("Wrong format of 'vote_id', got: {}".format(
                            initial_committee_info["vote_id"]))
                    else:
                        lcc.log_info("'vote_id' has correct format: vote_id_type")
                    self.check_uint256_numbers(response["result"], "total_votes", quiet=True)
                    check_that_entry("url", is_str(), quiet=True)
                    # todo: delete replace Bug ECHO-961
                    if not self.validator.is_eth_address(
                            initial_committee_info["eth_address"].replace("0000000000000000000000000000000000000000",
                                                                          "")):
                        lcc.log_error("Wrong format of 'eth_address', got: {}".format(
                            initial_committee_info["eth_address"].replace("0000000000000000000000000000000000000000",
                                                                          "")))
                    else:
                        lcc.log_info("'eth_address' has correct format: eth_address_type")
