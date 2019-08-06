# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that, is_true, is_false, not_equal_to, equal_to

from common.base_test import BaseTest
from project import ROPSTEN

SUITE = {
    "description": "Check for updating the list of active committee members"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("change_active_committee_member", "sidechain")
@lcc.suite("Check scenario 'Change active committee members'")
class ChangeActiveCommitteeMember(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def get_active_committee_members_ids(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        return self.get_response(response_id)["result"]["active_committee_members"]

    def get_active_committee_members_eth_addresses(self, active_committee_members_ids=None, print_log=True):
        if active_committee_members_ids is not None:
            active_committee_members_ids = [active_committee_members_ids]
        else:
            active_committee_members_ids = self.get_active_committee_members_ids()
        eth_addresses = []
        response_id = self.send_request(self.get_request("get_committee_members", [active_committee_members_ids]),
                                        self.__database_api_identifier)
        committee_members_objs = self.get_response(response_id)["result"]
        for i, committee_member_obj in enumerate(committee_members_objs):
            if committee_member_obj["id"] == active_committee_members_ids[i]:
                eth_addresses.append(committee_member_obj["eth_address"])
                if print_log:
                    lcc.log_info(
                        "'{}' active committee members has '{}' eth_address".format(active_committee_members_ids[i],
                                                                                    eth_addresses[i]))
        if len(eth_addresses) == 1:
            return eth_addresses[0]
        return eth_addresses

    def get_active_committee_members(self):
        return {"ids": self.get_active_committee_members_ids(),
                "eth_addresses": self.get_active_committee_members_eth_addresses()}

    def setup_suite(self):
        if not ROPSTEN:
            super().setup_suite()
            self._connect_to_ethereum()
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
        else:
            lcc.log_warn(
                "Tests did not run in the local network. Scenario 'change_active_committee_member' was skipped.")

    def teardown_suite(self):
        if not ROPSTEN:
            self._disconnect_to_echopy_lib()
            super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes the mechanism of updating the list of active addresses of committee members")
    def change_committee_eth_address_scenario(self, get_random_valid_account_name):
        if not ROPSTEN:
            new_account_name = get_random_valid_account_name
            new_account = new_account_name

            lcc.set_step("Get active committee members ids, ethereum addresses and store")
            active_committee_members = self.get_active_committee_members()
            active_committee_members_ids = active_committee_members["ids"]

            lcc.set_step("Get all committee members statuses. Store active committee members")
            for eth_address in active_committee_members["eth_addresses"]:
                committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3, eth_address)
                if not committee_member_status:
                    raise Exception("Active committee member with '{}' eth_address in the ECHO network "
                                    "do not compare with members in the Ethereum network".format(eth_address))
                lcc.log_info("Address '{}' is active: '{}'".format(eth_address, committee_member_status))

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

            lcc.set_step("Get ethereum address of created account in the Echo network")
            eth_account_address = self.utils.get_eth_address(self, new_account,
                                                             self.__database_api_identifier)["result"]["eth_addr"]
            lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

            lcc.set_step("Make new account committee member")
            broadcast_result = self.utils.perform_committee_member_create_operation(self, new_account,
                                                                                    eth_account_address,
                                                                                    self.__database_api_identifier)
            new_committee_member_account_id = self.get_operation_results_ids(broadcast_result)
            lcc.log_info("'{}' account became new committee member, "
                         "his committee member account id: '{}'".format(new_account, new_committee_member_account_id))

            lcc.set_step("Get info about object committee member account id")
            param = [new_committee_member_account_id]
            response_id = self.send_request(self.get_request("get_objects", [param]), self.__database_api_identifier)
            vote_id = self.get_response(response_id)["result"][0]["vote_id"]
            lcc.log_info("Vote id of new committee member: '{}'".format(vote_id))

            lcc.set_step("Get info about account and store")
            response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                            self.__database_api_identifier)
            account_info = self.get_response(response_id)["result"][0]
            lcc.log_info("Information about current '{}' account stored".format(self.echo_acc0))

            lcc.set_step("Perform 'account_update_operation' to vote for new committee member")
            account_info["options"]["votes"].append(vote_id)
            self.utils.perform_account_update_operation(self, self.echo_acc0, account_info,
                                                        self.__database_api_identifier)
            lcc.log_info("'{}' account vote for new '{}' committee member".format(self.echo_acc0, new_account))

            lcc.set_step("Waiting for maintenance and release of two blocks")
            self.wait_for_next_maintenance(self.__database_api_identifier, print_log=True)
            self.set_timeout_wait(wait_block_count=2)

            lcc.set_step("Get updated active committee members ids, ethereum addresses and store")
            updated_active_committee_members = self.get_active_committee_members()
            updated_active_committee_members_ids = updated_active_committee_members["ids"]

            lcc.set_step("Check that new committee member added. Store old and new committee members ids")
            require_that("'updated list of active committee members'", updated_active_committee_members_ids,
                         not_equal_to(active_committee_members_ids))
            old_member_id = set(active_committee_members_ids).difference(
                set(updated_active_committee_members_ids)).pop()
            new_member_id = set(updated_active_committee_members_ids).difference(
                set(active_committee_members_ids)).pop()
            require_that("'new committee member'", new_member_id, equal_to(new_committee_member_account_id))
            lcc.log_info(
                "Old committee member id: '{}', new committee member id: '{}'".format(old_member_id, new_member_id))

            lcc.set_step("Check that new committee member became active committee member, old - not active")
            old_member_address = self.get_active_committee_members_eth_addresses(old_member_id, print_log=False)
            new_member_address = self.get_active_committee_members_eth_addresses(new_member_id, print_log=False)
            lcc.log_info("'{}' old committee member address: '{}', '{}' new committee member address: '{}'"
                         "".format(old_member_id, old_member_address, new_member_id, new_member_address))

            new_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      new_member_address)
            check_that("'status of new committee member '{}''".format(new_member_address), new_committee_member_status,
                       is_true())

            old_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      old_member_address)
            check_that("'status of old committee member '{}''".format(old_member_address), old_committee_member_status,
                       is_false())

            lcc.set_step("Get info about object old committee member account id")
            old_committee_member_account_id = old_member_id
            param = [old_committee_member_account_id]
            response_id = self.send_request(self.get_request("get_objects", [param]), self.__database_api_identifier)
            vote_id = self.get_response(response_id)["result"][0]["vote_id"]
            lcc.log_info("Vote id of old committee member: '{}'".format(vote_id))

            lcc.set_step("Get info about account and store")
            response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                            self.__database_api_identifier)
            account_info = self.get_response(response_id)["result"][0]
            lcc.log_info("Information about current '{}' account stored".format(self.echo_acc0))

            lcc.set_step("Perform 'account_update_operation' to vote for old committee member")
            account_info["options"]["votes"] = [vote_id]
            self.utils.perform_account_update_operation(self, self.echo_acc0, account_info,
                                                        self.__database_api_identifier)
            lcc.log_info("'{}' account vote for old '{}' committee member".format(self.echo_acc0, old_member_id))

            lcc.set_step("Waiting for maintenance and release of two blocks")
            self.wait_for_next_maintenance(self.__database_api_identifier, print_log=True)
            self.set_timeout_wait(wait_block_count=2)

            lcc.set_step("Get updated active committee members ids, ethereum addresses and store")
            active_committee_members_ids = updated_active_committee_members_ids
            updated_active_committee_members = self.get_active_committee_members()
            updated_active_committee_members_ids = updated_active_committee_members["ids"]

            lcc.set_step("Check that old committee member added. Store old and new committee members ids")
            require_that("'updated list of active committee members'", updated_active_committee_members_ids,
                         not_equal_to(active_committee_members_ids))
            old_member_id = set(active_committee_members_ids).difference(
                set(updated_active_committee_members_ids)).pop()
            new_member_id = set(updated_active_committee_members_ids).difference(
                set(active_committee_members_ids)).pop()
            require_that("'new committee member'", new_member_id, equal_to(old_committee_member_account_id))
            lcc.log_info(
                "Old committee member id: '{}', new committee member id: '{}'".format(old_member_id, new_member_id))

            lcc.set_step("Check that new committee member became not active committee member, old - active")
            old_member_address = self.get_active_committee_members_eth_addresses(old_member_id, print_log=False)
            new_member_address = self.get_active_committee_members_eth_addresses(new_member_id, print_log=False)
            lcc.log_info("'{}' old committee member address: '{}', '{}' new committee member address: '{}'"
                         "".format(old_member_id, old_member_address, new_member_id, new_member_address))

            new_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      new_member_address)
            check_that("'status of new committee member '{}''".format(new_member_address), new_committee_member_status,
                       is_true())

            old_committee_member_status = self.eth_trx.get_status_of_committee_member(self, self.web3,
                                                                                      old_member_address)
            check_that("'status of old committee member '{}''".format(old_member_address), old_committee_member_status,
                       is_false())
        else:
            lcc.log_warn(
                "Tests did not run in the local network. Scenario 'change_active_committee_member' was skipped.")
