# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Entering the currency ethereum in the network ECHO to the account"
}


@lcc.prop("testing", "main")
@lcc.tags("sidechain", "eth_to_echo")
@lcc.suite("Check scenario 'Ethereum in'")
class EthToEcho(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    @staticmethod
    def get_random_int(_to, _from=1):
        return random.randrange(_from, _to)

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario entering eth assets to the echo account")
    def ethereum_in_scenario(self, get_random_valid_account_name, get_random_float_up_to_hundred):
        new_account = get_random_valid_account_name
        min_eth_amount = 0.01
        eth_amount = get_random_float_up_to_hundred

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
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=eth_account_address,
                                                            value=min_eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get updated account balance in ethereum after first in")
        ethereum_balance_first_in = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier)

        check_that(
            "'updated balance in ethereum'",
            ethereum_balance_first_in["amount"],
            is_(self.utils.convert_ethereum_to_eeth(min_eth_amount) - self.utils.convert_ethereum_to_eeth(unpaid_fee))
        )

        lcc.set_step("Second send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=eth_account_address, value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get updated account balance in ethereum after second in")
        ethereum_balance_second_in = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                                     self.eth_asset)
        check_that(
            "'updated balance in ethereum'",
            ethereum_balance_second_in["amount"],
            is_(ethereum_balance_first_in["amount"] + self.utils.convert_ethereum_to_eeth(eth_amount))
        )

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario transferring eeth between accounts")
    def transfer_eeth_scenario(self, get_random_valid_account_name, get_random_float_up_to_hundred):
        new_account = get_random_valid_account_name
        eth_amount = get_random_float_up_to_hundred

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier,
                                                          log_broadcast=False)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"][0]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get new account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier)["amount"]
        lcc.log_info("New account '{}' balance in ethereum is '{}'".format(new_account, ethereum_balance))

        lcc.set_step("Get recipient balance in ethereum before transfer")
        recipient_balance_before_transfer = self.utils.get_account_balances(self, self.echo_acc0,
                                                                            self.__database_api_identifier,
                                                                            self.eth_asset)["amount"]
        lcc.log_info("Recipient '{}' balance before "
                     "transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance_before_transfer))

        lcc.set_step("Transfer eeth from account to account")
        transfer_amount = self.get_random_int(_to=ethereum_balance)
        self.utils.perform_transfer_operations(self, new_account, self.echo_acc0, self.__database_api_identifier,
                                               transfer_amount=transfer_amount, amount_asset_id=self.eth_asset)
        lcc.log_info("Transfer operation performed")

        lcc.set_step("Get recipient balance in ethereum after transfer")
        recipient_balance_after_transfer = self.utils.get_account_balances(self, self.echo_acc0,
                                                                           self.__database_api_identifier,
                                                                           self.eth_asset)["amount"]
        lcc.log_info("Recipient '{}' balance after "
                     "transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance_after_transfer))

        lcc.set_step("Checking that sent eeth assets have been delivered")
        check_that(
            "'updated balance in ethereum'",
            recipient_balance_after_transfer,
            is_(recipient_balance_before_transfer + transfer_amount)
        )
