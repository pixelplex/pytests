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
        self.new_account = None

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
    @lcc.tags("Bug ECHO-1043")
    @lcc.test("The scenario checks the main parts before testing the ERC20 sidechain functionality")
    def erc20_sidechain_pre_run_scenario(self, get_random_valid_account_name, get_random_string,
                                         get_random_valid_asset_name):
        self.new_account = get_random_valid_account_name
        name = "erc20" + get_random_string
        symbol = get_random_valid_asset_name

        lcc.set_step("Create and get new account")
        self.new_account = self.get_account_id(self.new_account, self.__database_api_identifier,
                                               self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(self.new_account))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        deployment = self.eth_trx.deploy_contract_in_ethereum_network(self, eth_account=self.eth_address,
                                                                      contract_abi=self.erc20_abi,
                                                                      contract_bytecode=self.erc20_contract)
        contract = deployment.get("contract_instance")
        contract_address = deployment.get("contract_address")
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(contract_address))

        lcc.set_step("Get ethereum account ERC20 tokens balance in the Ethereum network")
        ethereum_er20_balance = self.eth_trx.get_balance_of(contract, self.eth_address)

        lcc.set_step("Perform register erc20 operation")
        bd_result = self.utils.perform_register_erc20_token_operation(self, account=self.new_account,
                                                                      eth_addr=contract_address[2:], name=name,
                                                                      symbol=symbol, decimals=8,
                                                                      database_api_id=self.__database_api_identifier,
                                                                      log_broadcast=True)
