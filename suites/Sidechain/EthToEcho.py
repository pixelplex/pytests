# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

from common.base_test import BaseTest

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
        eth_amount_1 = 0.01
        eth_amount_2 = 0.02

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get account balance in ethereum of new account")
        ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                           self.eth_asset)
        check_that(
            "'balance in ethereum'",
            ethereum_balance["amount"],
            is_(0)
        )

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier,
                                                          log_broadcast=False)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"][0]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Get unpaid fee for ethereum address creation")
        unpaid_fee = self.utils.get_unpaid_fee(self, new_account)

        lcc.set_step("First send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=eth_account_address, value=eth_amount_1)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction, log_transaction=True)

        lcc.set_step("Get updated account balance in ethereum after first in")
        ethereum_balance_first_in = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier)

        check_that(
            "'updated balance in ethereum'",
            ethereum_balance_first_in["amount"],
            is_(self.utils.convert_ethereum_to_eeth(eth_amount_1) - self.utils.convert_ethereum_to_eeth(unpaid_fee))
        )

        lcc.set_step("Second send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=eth_account_address, value=eth_amount_2)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction, log_transaction=True)

        lcc.set_step("Get updated account balance in ethereum after second in")
        ethereum_balance_second_in = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                                     self.eth_asset)
        check_that(
            "'updated balance in ethereum'",
            ethereum_balance_second_in["amount"],
            is_(ethereum_balance_first_in["amount"] + self.utils.convert_ethereum_to_eeth(eth_amount_2))
        )

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
