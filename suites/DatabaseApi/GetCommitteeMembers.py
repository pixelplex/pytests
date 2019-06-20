# -*- coding: utf-8 -*-
import json

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import has_length, require_that, this_dict, check_that, check_that_entry, is_str, \
    is_integer

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
        response = self.get_response(response_id, log_response=True)
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
                        lcc.log_info("'committee_member_account' has correct format: account_object_type")
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

    @lcc.prop("testing", "positive")
    # todo: add when added 0.7 changes
    @lcc.hidden()
    @lcc.tags("database_api", "get_committee_members")
    @lcc.suite("Positive testing of method 'get_committee_members'", rank=2)
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
        @lcc.test("Create account new committee member")
        @lcc.depends_on("DatabaseApi.GetCommitteeMembers.GetCommitteeMembers.method_main_check")
        def get_info_about_created_committee_member(self, get_random_valid_account_name, get_random_string):
            new_account = get_random_valid_account_name
            url = get_random_string

            lcc.set_step("Register new account in the network")
            new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                              self.__registration_api_identifier)
            lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

            lcc.set_step("Make new account lifetime member")
            self.utils.perform_account_upgrade_operation(self, new_account, self.__database_api_identifier)
            lcc.log_info("New '{}' account became lifetime member".format(new_account))

            lcc.set_step("Generate ethereum address for new account")
            self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier)
            lcc.log_info("Ethereum address for '{}' account generated successfully".format(new_account))

            lcc.set_step("Get ethereum address of created account in the network")
            eth_account_address = self.utils.get_eth_address(self, new_account,
                                                             self.__database_api_identifier)["result"]["eth_addr"]
            lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

            lcc.set_step("Make new account committee member")
            broadcast_result = self.utils.perform_committee_member_create_operation(self, new_account,
                                                                                    eth_account_address,
                                                                                    self.__database_api_identifier)
            committee_member_account_id = self.get_operation_results_ids(broadcast_result)
            lcc.log_info("'{}' account became new committee member, "
                         "his committee member account id: '{}'".format(new_account, committee_member_account_id))

            lcc.set_step("Get info about new committee member")
            param = [committee_member_account_id]
            response_id = self.send_request(self.get_request("get_committee_members", [param]),
                                            self.__database_api_identifier)
            response = self.get_response(response_id, log_response=True)
            lcc.log_info("Call method 'get_committee_members' with params: {}".format(param))

            lcc.set_step("Check new committee member info")
            committee_member_info = response["result"][0]
            with this_dict(committee_member_info):
                check_that_entry("id", is_str(committee_member_account_id), quiet=True)
                check_that_entry("committee_member_account", is_str(new_account), quiet=True)
                check_that_entry("total_votes", is_integer(0), quiet=True)
                check_that_entry("url", is_str(url), quiet=True)
                # todo: delete replace Bug ECHO-961
                check_that_entry("eth_address",
                                 is_str(eth_account_address.replace("0000000000000000000000000000000000000000",
                                                                    "")), quiet=True)
