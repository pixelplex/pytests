# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_erc20_account_deposits(account)'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("database_api", "get_erc20_account_deposits", "sidechain")
@lcc.suite("Check work of method 'get_erc20_account_deposits'", rank=1)
class GetERC20AccountDeposits(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_account = None
        self.erc20_contract_code = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")

    def setup_suite(self):
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
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_erc20_account_deposits'")
    def method_main_check(self, get_random_string, get_random_valid_asset_name, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        contract_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name
        ecr20_amount = 1

        lcc.set_step("Deploy ECR20 contract in the Ethereum network")
        ecr20_contract = self.eth_trx.deploy_contract_in_ethereum_network(self.web3,
                                                                          eth_address=self.eth_account.address,
                                                                          contract_abi=self.erc20_abi,
                                                                          contract_bytecode=self.erc20_contract_code)
        lcc.log_debug(str(self.eth_account.address))
        lcc.log_info("ERC20 contract crated in the Ethereum network, address: {}".format(ecr20_contract.address))

        lcc.set_step("Perform register erc20 token operation")
        operation_result = self.utils.perform_register_erc20_token_operation(self, account=self.echo_acc0,
                                                                             eth_addr=ecr20_contract.address,
                                                                             name=contract_name,
                                                                             symbol=erc20_symbol,
                                                                             database_api_id=self.
                                                                             __database_api_identifier,
                                                                             log_broadcast=True)
        lcc.log_info("Call method 'get_erc20_token' with eth_erc20_contract_address='0.0.0' parameter")

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [ecr20_contract.address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id, log_response=True)["result"]
        lcc.log_info("Called method 'get_erc20_token' with ERC20 contract address: {}".format(result["eth_addr"]))

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Get ethereum account ERC20 tokens balance in the Ethereum network")
        in_ethereum_erc20_balance = self.eth_trx.get_balance_of(self.erc20_contract, self.eth_account.address)
        lcc.log_debug(str(in_ethereum_erc20_balance))