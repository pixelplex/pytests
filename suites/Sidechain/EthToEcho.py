# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

from common.base_test import BaseTest
from project import BLOCK_RELEASE_INTERVAL

SUITE = {
    "description": "Entering the currency ethereum in the network ECHO to the account"
}


@lcc.prop("testing", "main")
@lcc.tags("eth_in")
# @lcc.hidden()
@lcc.suite("Check scenario 'Ethereum in'")
class EthToEcho(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.temp_count = 0
        self.block_count = 10
        self.waiting_time_result = 0

    def get_eth_address(self, account_id, timeout=BLOCK_RELEASE_INTERVAL):
        self.temp_count += 1
        response_id = self.send_request(self.get_request("get_eth_address", [account_id]),
                                        self.__database_api_identifier, debug_mode=True)
        response = self.get_response(response_id, log_response=True)
        if response["result"]:
            return response
        if self.temp_count <= self.block_count:
            self.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_eth_address(account_id, timeout=timeout)
        raise Exception("No ethereum address of '{}' account. "
                        "Waiting time result='{}'".format(account_id, self.waiting_time_result))

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario entering eth assets to the echo account")
    def ethereum_in_scenario(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        # tx_hash = "0x46cf8218792c59d93dabc738198b98a8d556ae26bbffb7be8e918b41f9cb33da"
        #
        # tx = self.web3.eth.getTransaction(tx_hash)
        # print("TRANZA:\n" + str(tx))
        #
        # tx_logs = self.web3.eth.getTransactionReceipt(tx_hash).logs
        # print("LOGS:\n" + str(tx_logs))

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                           self.eth_asset)
        check_that(
            "'balance in ethereum'",
            ethereum_balance["amount"],
            is_(0)
        )

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier,
                                                          log_broadcast=True)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.get_eth_address(new_account)["result"][0]["eth_addr"]

        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        print("\nAccount: '{}'".format(new_account))
        print("\nEth address: '{}'".format(eth_account_address))

        # todo: ethereum steps
        # Steps:
        # todo: send eth to echo from main account 1
        # todo: check echo account balance 1
        # todo: send eth to echo from main account 2
        # todo: check echo account balance 2
        # todo: transfer eth in network to another account
        # todo: transfer eth in network to another account address 1
        # todo: transfer eth in network to another account address 2
        # todo: to yourself ?
        # todo: withdraw
