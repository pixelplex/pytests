# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Entering the currency ERC20 token in the network ECHO to the account and withdraw that currency"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("sidechain_erc20")
@lcc.suite("Check scenario 'ERC20ToEcho and ERC20FromEchoToEth'")
class ERC20(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.eth_address = None
        self.erc20_contract = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")

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
    @lcc.test("The scenario checks the main parts before testing the ERC20 sidechain functionality")
    def erc20_sidechain_pre_run_scenario(self, get_random_string, get_random_valid_asset_name):
        name = "erc20" + get_random_string
        symbol = get_random_valid_asset_name

        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        ERC20 = self.web3.eth.contract(abi=self.erc20_abi, bytecode=self.erc20_contract)
        tx_hash = ERC20.constructor().transact()
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)

        erc20 = self.web3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=self.erc20_abi,
        )

        print("\nAccount balance: {}".format(erc20.functions.balanceOf(self.web3.eth.accounts[0]).call()))

        erc20_address = tx_receipt.contractAddress[2:]
        operation = self.echo_ops.get_register_erc20_token_operation(echo=self.echo, account=self.echo_acc0,
                                                                     eth_addr=erc20_address, name=name, symbol=symbol,
                                                                     decimals=8)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, debug_mode=True)
