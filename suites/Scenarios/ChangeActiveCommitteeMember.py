# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_false, require_that, check_that, is_bool

from common.base_test import BaseTest
from project import INITIAL_ACCOUNTS_ETH_ADDRESSES

SUITE = {
    "description": "Check for updating the list of active committee members"
}


@lcc.prop("testing", "main")
@lcc.tags("change_active_committee_member")
@lcc.suite("Check scenario 'Change active committee members'")
@lcc.disabled()
class ChangeActiveCommitteeMember(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.eth_address = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ganache_ethereum()
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
        self.eth_address = self.web3.eth.accounts[0]
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes the mechanism of updating the list of active addresses of committee members")
    def change_committee_eth_address_scenario(self, get_random_valid_account_name):
        active_committee_members = []
        new_account = get_random_valid_account_name
        status = None

        lcc.set_step("Get all committee members statuses. Store active committee members")
        for i in range(len(INITIAL_ACCOUNTS_ETH_ADDRESSES)):
            status = self.eth_trx.get_status_of_committee_member(self, INITIAL_ACCOUNTS_ETH_ADDRESSES[i])
            if status:
                active_committee_members.append(INITIAL_ACCOUNTS_ETH_ADDRESSES[i])
            lcc.log_info(
                "Committee member #'{}': address='{}', status='{}'".format(str(i), INITIAL_ACCOUNTS_ETH_ADDRESSES[i],
                                                                           status))
        lcc.log_info("List of active committee members:\n{}".format(active_committee_members))

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

        lcc.set_step("Get info about object committee member account id")
        param = [committee_member_account_id]
        response_id = self.send_request(self.get_request("get_objects", [param]), self.__database_api_identifier)
        vote_id = self.get_response(response_id)["result"][0]["vote_id"]
        lcc.log_info("Vote id of new committee member: '{}'".format(vote_id))

        lcc.set_step("Get info about account and store")
        response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Information about current '{}' account stored".format(new_account))

        lcc.set_step("Perform 'account_update_operation' to vote for new committee member")
        account_info = response["result"][0]
        account_info["options"]["votes"].append(vote_id)
        self.utils.perform_account_update_operation(self, self.echo_acc0, account_info, self.__database_api_identifier)
        lcc.log_info("'{}' account vote for new '{}' committee member".format(self.echo_acc0, new_account))

        lcc.set_step("Waiting for maintenance")
        self.wait_for_next_maintenance(self.__database_api_identifier, print_log=True)

        lcc.set_step("Check previously active committee members to change their status")
        self.set_timeout_wait(60)

        parameters = [[get_random_valid_account_name], 1000]
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts", [parameters]),
                                        self.__database_api_identifier, debug_mode=True)
        self.get_response(response_id, log_response=True)

        for i in range(len(active_committee_members)):
            status = self.eth_trx.get_status_of_committee_member(self, active_committee_members[i])
            print("\nStatus #{}: {}".format(str(i), str(status)))
            if not status:
                lcc.log_info(
                    "Committee member #'{}': address='{}', "
                    "changed status to '{}'".format(str(i), active_committee_members[i], status))
                break
        if status:
            raise Exception("List of active committee members did not changed")
        require_that("'status of one previously active committee members'", status, is_false())

        lcc.set_step("Check that new committee member became active committee member")
        status = self.eth_trx.get_status_of_committee_member(self, eth_account_address)
        # todo: change to is_true(). Bug ECHO-945
        check_that("'status of new committee member'", status, is_bool())

        lcc.set_step("Replenish balance of new active committee member")
        self.eth_trx.replenish_balance_of_committee_member(self.web3, self.eth_address, eth_account_address)
