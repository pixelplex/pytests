# -*- coding: utf-8 -*-
import json

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, this_dict, check_that, check_that_entry, is_str

from common.base_test import BaseTest
from project import GENESIS

SUITE = {
    "description": "Method 'get_committee_members'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_committee_members")
@lcc.suite("Check work of method 'get_committee_members'", rank=1)
class GetCommitteeMembers(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_committee_members'")
    def method_main_check(self):
        # todo: remove 'json.load(open())' when added 0.7 changes
        min_committee_member_count = json.load(open(GENESIS))["immutable_parameters"]["min_committee_member_count"]
        committee_members_ids = []

        lcc.set_step("Get info about default committee members")
        for i in range(min_committee_member_count):
            committee_members_ids.append(self.get_object_type(self.echo.config.object_types.COMMITTEE_MEMBER) + str(i))
        response_id = self.send_request(self.get_request("get_committee_members", [committee_members_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_committee_members' with params: {}".format(committee_members_ids))

        lcc.set_step("Check length of received committee members")
        require_that(
            "'list of received accounts'",
            response["result"], has_length(len(committee_members_ids))
        )

        for i in range(len(response["result"])):
            lcc.set_step("Check committee member #{} - '{}'".format(i, committee_members_ids[i]))
            committee_member_info = response["result"][i]
            with this_dict(committee_member_info):
                if check_that("committee_member_info", committee_member_info, has_length(7)):
                    check_that_entry("id", is_str(committee_members_ids[i]), quiet=True)
                    if not self.validator.is_account_id(committee_member_info["committee_member_account"]):
                        lcc.log_error("Wrong format of 'committee_member_account', got: {}".format(
                            committee_member_info["membership_expiration_date"]))
                    else:
                        lcc.log_info("'committee_member_account' has correct format: committee_member_object_type")
                    if not self.validator.is_vesting_balance_id(committee_member_info["pay_vb"]):
                        lcc.log_error("Wrong format of 'pay_vb', got: {}".format(
                            committee_member_info["pay_vb"]))
                    else:
                        lcc.log_info("'pay_vb' has correct format: vesting_balance_object_type")
                    if not self.validator.is_vote_id(committee_member_info["vote_id"]):
                        lcc.log_error("Wrong format of 'vote_id', got: {}".format(
                            committee_member_info["vote_id"]))
                    else:
                        lcc.log_info("'vote_id' has correct format: vote_id_type")
                    self.check_uint256_numbers(response["result"][i], "total_votes", quiet=True)
                    check_that_entry("url", is_str(), quiet=True)
                    # todo: delete replace Bug ECHO-961
                    if not self.validator.is_eth_address(
                            committee_member_info["eth_address"].replace("0000000000000000000000000000000000000000",
                                                                         "")):
                        lcc.log_error("Wrong format of 'eth_address', got: {}".format(
                            committee_member_info["eth_address"].replace("0000000000000000000000000000000000000000",
                                                                         "")))
                    else:
                        lcc.log_info("'eth_address' has correct format: eth_address_type")

