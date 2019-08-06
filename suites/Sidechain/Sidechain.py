# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Entering the currency ethereum in the network ECHO to the account"
}


@lcc.prop("testing", "main")
@lcc.tags("sidechain")
@lcc.suite("Check scenario 'Ethereum in'")
class Sidechain(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.new_account = None
        self.eth_address = None
        self.eth_account_address = None
        self.temp_count = 0

    @staticmethod
    def get_random_amount(_to, _from=0.01):
        return round(random.uniform(_from, _to))

    def withdraw_eth_to_ethereum_address(self, from_account, withdraw_amount):
        lcc.set_step("Get address balance in ethereum network")
        eth_address_balance = self.utils.get_address_balance_in_eth_network(self, self.eth_address, currency="wei")
        lcc.log_info("Ethereum address has '{}' balance in ethereum".format(eth_address_balance))

        lcc.set_step("Withdraw eth to ethereum address")
        self.utils.perform_withdraw_eth_operation_operation(self, from_account, self.eth_address[2:],
                                                            withdraw_amount, self.__database_api_identifier,
                                                            log_broadcast=True)

        lcc.set_step("Get updated address balance in ethereum network")
        eth_address_balance_after_withdraw = self.utils.get_updated_address_balance_in_eth_network(self,
                                                                                                   self.eth_address,
                                                                                                   eth_address_balance,
                                                                                                   currency="wei")
        lcc.log_info("Ethereum address has '{}' balance in ethereum".format(eth_address_balance_after_withdraw))

        lcc.set_step("Check that withdraw eth completed successfully")
        check_that(
            "'updated address balance in ethereum'",
            int(eth_address_balance_after_withdraw),
            equal_to(int(eth_address_balance) + self.utils.convert_eeth_to_currency(withdraw_amount, currency="wei"))
        )

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
    @lcc.test("The scenario checks the main parts before testing the sidechain functionality")
    def sidechain_pre_run_scenario(self, get_random_valid_account_name):
        self.new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        self.new_account = self.get_account_id(self.new_account, self.__database_api_identifier,
                                               self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account))

        lcc.set_step("Get account balance in ethereum of new account")
        ethereum_balance = self.utils.get_account_balances(self, self.new_account, self.__database_api_identifier,
                                                           self.eth_asset)
        check_that(
            "'balance in ethereum'",
            ethereum_balance["amount"],
            equal_to(0)
        )

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, self.new_account, self.__database_api_identifier,
                                                          log_broadcast=False)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        self.eth_account_address = self.utils.get_eth_address(self, self.new_account,
                                                              self.__database_api_identifier)["result"][0]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(self.new_account, self.eth_account_address))

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario entering eth assets to the echo account")
    @lcc.depends_on("Sidechain.Sidechain.Sidechain.sidechain_pre_run_scenario")
    def ethereum_in_scenario(self, get_random_float_up_to_ten):
        min_eth_amount = 0.01
        eth_amount = get_random_float_up_to_ten

        lcc.set_step("Get unpaid fee for ethereum address creation")
        unpaid_fee = self.utils.get_unpaid_fee(self, self.new_account)

        lcc.set_step("First send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=self.eth_account_address,
                                                            value=min_eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get updated account balance in ethereum after first in")
        ethereum_balance_first_in = self.utils.get_eth_balance(self, self.new_account, self.__database_api_identifier)[
            "amount"]

        check_that(
            "'updated balance in ethereum'",
            ethereum_balance_first_in,
            equal_to(self.utils.convert_ethereum_to_eeth(min_eth_amount) - unpaid_fee)
        )

        lcc.set_step("Second send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=self.eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get updated account balance in ethereum after second in")
        ethereum_balance_second_in = self.utils.get_account_balances(self, self.new_account,
                                                                     self.__database_api_identifier,
                                                                     self.eth_asset)["amount"]
        check_that(
            "'updated balance in ethereum'",
            ethereum_balance_second_in,
            equal_to(ethereum_balance_first_in + self.utils.convert_ethereum_to_eeth(eth_amount))
        )

        lcc.set_step("Withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=ethereum_balance_second_in)
        lcc.log_info("Withdrawing '{}' eeth from '{}' account".format(withdraw_amount, self.new_account))
        self.withdraw_eth_to_ethereum_address(self.new_account, withdraw_amount)

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario transferring eeth between accounts")
    @lcc.depends_on("Sidechain.Sidechain.Sidechain.sidechain_pre_run_scenario")
    def transfer_eeth_scenario(self, get_random_float_up_to_ten):
        eth_amount = get_random_float_up_to_ten

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=self.eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, self.new_account, self.__database_api_identifier)["amount"]
        lcc.log_info("Account '{}' balance in ethereum is '{}'".format(self.new_account, ethereum_balance))

        lcc.set_step("Get recipient balance in ethereum before transfer")
        recipient_balance = self.utils.get_account_balances(self, self.echo_acc0, self.__database_api_identifier,
                                                            self.eth_asset)["amount"]
        lcc.log_info(
            "Recipient '{}' balance before transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance))

        lcc.set_step("Transfer eeth from account to recipient")
        transfer_amount = self.get_random_amount(_to=ethereum_balance)
        self.utils.perform_transfer_operations(self, self.new_account, self.echo_acc0, self.__database_api_identifier,
                                               transfer_amount=transfer_amount, amount_asset_id=self.eth_asset)
        lcc.log_info("Transfer operation performed")

        lcc.set_step("Get recipient balance in ethereum after transfer")
        recipient_balance_after_transfer = self.utils.get_eth_balance(self, self.echo_acc0,
                                                                      self.__database_api_identifier)["amount"]
        lcc.log_info("Recipient '{}' balance after "
                     "transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance_after_transfer))

        lcc.set_step("Checking that sent eeth assets have been delivered")
        check_that(
            "'updated balance in ethereum'",
            recipient_balance_after_transfer,
            equal_to(recipient_balance + transfer_amount)
        )

        lcc.set_step("Withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=recipient_balance_after_transfer)
        lcc.log_info("Withdrawing '{}' eeth from '{}' account".format(withdraw_amount, self.echo_acc0))
        self.withdraw_eth_to_ethereum_address(self.echo_acc0, withdraw_amount)

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario transferring eeth to account addresses")
    @lcc.depends_on("Sidechain.Sidechain.Sidechain.sidechain_pre_run_scenario")
    def transfer_eeth_to_account_address_scenario(self, get_random_float_up_to_ten, get_random_string):
        eth_amount = get_random_float_up_to_ten
        label = get_random_string
        addresses_count = 2
        account_address_object = []
        account_addresses = []

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=self.eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, self.new_account, self.__database_api_identifier)["amount"]
        lcc.log_info("Account '{}' balance in ethereum is '{}'".format(self.new_account, ethereum_balance))

        lcc.set_step("Get recipient balance in ethereum before transfer")
        recipient_balance = self.utils.get_account_balances(self, self.echo_acc0, self.__database_api_identifier,
                                                            self.eth_asset)["amount"]
        lcc.log_info(
            "Recipient '{}' balance before transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance))

        lcc.set_step("Create multiple account address for new account")
        for i in range(addresses_count):
            broadcast_result = self.utils.perform_account_address_create_operation(self, self.echo_acc0, label + str(i),
                                                                                   self.__database_api_identifier)
            account_address_object.append(self.get_operation_results_ids(broadcast_result))

        # todo: change to 'get_account_addresses'. Bug: "ECHO-843"
        lcc.set_step("Get objects 'impl_account_address_object_type' and store addresses")
        for i in range(len(account_address_object)):
            param = [[account_address_object[i]]]
            response_id = self.send_request(self.get_request("get_objects", param), self.__database_api_identifier)
            account_addresses.append(self.get_response(response_id)["result"][0]["address"])

        lcc.set_step("Transfer eeth assets via first account_address")
        transfer_amount = self.get_random_amount(_to=ethereum_balance)
        self.utils.perform_transfer_to_address_operations(self, self.new_account, account_addresses[0],
                                                          self.__database_api_identifier,
                                                          transfer_amount=transfer_amount,
                                                          amount_asset_id=self.eth_asset, log_broadcast=True)

        lcc.set_step("Get account balance after transfer and store")
        recipient_balance_after_transfer = self.utils.get_eth_balance(self, self.echo_acc0,
                                                                      self.__database_api_identifier)["amount"]
        lcc.log_info("Recipient '{}' balance after "
                     "transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance_after_transfer))

        lcc.set_step("Check that transfer assets completed successfully")
        check_that(
            "'updated recipient balance in ethereum'",
            recipient_balance_after_transfer,
            equal_to(recipient_balance + transfer_amount)
        )

        lcc.set_step("Transfer assets via second account_address")
        transfer_amount = self.get_random_amount(_to=ethereum_balance - transfer_amount)
        self.utils.perform_transfer_to_address_operations(self, self.new_account, account_addresses[1],
                                                          self.__database_api_identifier,
                                                          transfer_amount=transfer_amount,
                                                          amount_asset_id=self.eth_asset, log_broadcast=True)

        lcc.set_step("Get account balance after second transfer and store")
        recipient_balance_after_second_transfer = self.utils.get_eth_balance(self, self.echo_acc0,
                                                                             self.__database_api_identifier)["amount"]
        lcc.log_info("Recipient '{}' balance after second "
                     "transfer in ethereum is '{}'".format(self.echo_acc0, recipient_balance_after_second_transfer))

        lcc.set_step("Check that second transfer assets completed successfully")
        check_that(
            "'updated recipient balance in ethereum'",
            recipient_balance_after_second_transfer,
            equal_to(recipient_balance_after_transfer + transfer_amount)
        )

        lcc.set_step("Withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=recipient_balance_after_second_transfer)
        lcc.log_info("Withdrawing '{}' eeth from '{}' account".format(withdraw_amount, self.echo_acc0))
        self.withdraw_eth_to_ethereum_address(self.echo_acc0, withdraw_amount)
