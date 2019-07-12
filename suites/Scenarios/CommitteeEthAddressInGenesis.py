# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, check_that, is_

from common.base_test import BaseTest
from project import GENESIS

SUITE = {
    "description": "Check the possibility to indicate the eth_address of the committee in the genesis"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("eth_address_in_genesis")
@lcc.suite("Check scenario 'Committee ethereum addresses in genesis file'")
class CommitteeEthAddressInGenesis(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario checks possibility to indicate the eth_address in the genesis.")
    def eth_address_in_genesis_scenario(self):
        initial_committee_candidates = GENESIS["initial_committee_candidates"]
        committee_members_names = []
        committee_members_eth_addresses = []
        committee_members_ids = []
        committee_members_eth_addresses_echo = []

        lcc.set_step("Get committees members names and eth_addresses from genesis file")
        for i in range(len(initial_committee_candidates)):
            committee_members_names.append(GENESIS["initial_committee_candidates"][i]["owner_name"])
            committee_members_eth_addresses.append(GENESIS["initial_committee_candidates"][i]["eth_address"])
            lcc.log_info("Committee member #{}: name='{}', eth_address='{}'".format(str(i), committee_members_names[i],
                                                                                    committee_members_eth_addresses[i]))

        lcc.set_step("Get committee members from ECHO network and store their ids")
        params = [committee_members_names[0], len(committee_members_names)]
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        for i in range(len(response)):
            if response[i][0] == committee_members_names[i]:
                committee_members_ids.append(response[i][1])
        require_that("'stored committee_members_ids count'", committee_members_ids,
                     has_length(len(committee_members_names)))
        lcc.log_info("Stored committee members ids: '{}'".format(str(committee_members_ids)))

        lcc.set_step("Get committee members eth_addresses from ECHO network and store")
        response_id = self.send_request(self.get_request("get_objects", [committee_members_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        for i in range(len(response)):
            committee_members_eth_addresses_echo.append(response[i]["eth_address"])
            lcc.log_info("Committee member #'{}' eth_addresses in Echo: '{}'".format(str(i), str(
                committee_members_eth_addresses_echo[i])))

        lcc.set_step("Compare eth_addresses in genesis and ECHO network")
        for i in range(len(committee_members_eth_addresses)):
            check_that("'eth_addresses of committee members'", committee_members_eth_addresses[i],
                       is_(committee_members_eth_addresses_echo[i]))
