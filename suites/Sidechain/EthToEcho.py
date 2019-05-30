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

        # # todo: ethereum steps
        # lcc.set_step("Send ethereum_amount from Eth to Echo")
        # ethereum_amount = 9
        # web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        # status = web3.isConnected()
        # print("\nis_connected: " + str(status))
        #
        # web3.eth.defaultAccount = web3.eth.account[0] # todo: not need private_key ?
        #
        # block_num = web3.eth.blockNumber
        # print("\nblock_num is: " + str(block_num))
        # account_balance_in_wei = web3.eth.getBalance("0x1AFeEcE88325110488570146f2635C8615Ad0613")
        # print("\naccount_balance_in_wei: " + str(account_balance_in_wei))
        # account_balance_in_eth = web3.fromWei(account_balance_in_wei, 'ether')
        # print("\naccount_balance_in_eth: " + str(account_balance_in_eth))
        #
        # address = web3.toChecksumAddress("0xfA562F151a8D7cD62A4b0ca53aCF108CAe4497cF")
        # contract = web3.eth.contract(address=address)
        # print("\nsidechain contract: " + str(contract))
        #
        # account_1 = "0x1AFeEcE88325110488570146f2635C8615Ad0613"
        # # todo: don't have address of account2
        # account_2 = None
        #
        # # todo: don't have private_key of account1
        # private_key_account_1 = None
        #
        # nonce = web3.eth.getBlockTransactionCount(account_1)
        #
        # tx = {
        #     "nonce": nonce,
        #     "to": account_2,
        #     "value": web3.toWei(1, "ether"),
        #     "gas": 2000000,
        #     "gasPrice": web3.toWei("50", 'qwei')
        # }
        #
        # signed_tx = web3.eth.account.signTransaction(tx, private_key_account_1)
        # tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # print(web3.toHex(tx_hash))

        # lcc.set_step("Get updated ethereum balance")
        # ethereum_balance = self.utils.get_account_balances(self, "1.2.329", self.__database_api_identifier,
        #                                                    self.eth_asset)
        # check_that(
        #     "'balance in ethereum'",
        #     ethereum_balance["amount"],
        #     is_(10000)
        # )
        #
        # new_account = get_random_valid_account_name
        # ethereum_amount = 9
        #
        # lcc.set_step("Create and get new account")
        # new_account = self.get_account_id(new_account, self.__database_api_identifier,
        #                                   self.__registration_api_identifier)
        # lcc.log_info("New Echo account created, account_id='{}'".format(new_account))
        #
        # operation = self.echo_ops.get_transfer_operation(self.echo, from_account_id="1.2.329",
        #                                                  to_account_id=new_account, amount=100, amount_asset_id="1.3.1",
        #                                                  debug_mode=True)
        # collected_operation = self.collect_operations(operation, self.__database_api_identifier, fee_asset_id="1.3.1")
        # broadcast_result = self.echo_ops.broadcast(self.echo, list_operations=collected_operation,
        #                                            log_broadcast=True)
        #
        # lcc.set_step("Get updated ethereum balance")
        # ethereum_balance = self.utils.get_account_balances(self, "1.2.329", self.__database_api_identifier,
        #                                                    self.eth_asset)
        #
        # lcc.set_step("Get updated ethereum balance")
        # ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
        #                                                    self.eth_asset)
