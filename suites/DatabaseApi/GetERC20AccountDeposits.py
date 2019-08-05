# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than

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
        self.__history_api_identifier = None
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_account = None
        self.erc20_contract_code = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")

    @staticmethod
    def get_random_amount(_to, _from=0):
        return random.randrange(_from, _to)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}',"
            " history='{}'".format(self.__database_api_identifier,
                                   self.__registration_api_identifier,
                                   self.__history_api_identifier))
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
        new_account_name = get_random_valid_account_name
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name
        sidechain_issue_operations = []
        erc20_deposit_amounts = []

        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(new_account_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account_id, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get ethereum address of created account in the ECHO network")
        eth_account_address = self.utils.get_eth_address(self, new_account_id,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account_id, eth_account_address))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(self.web3,
                                                                          eth_address=self.eth_account.address,
                                                                          contract_abi=self.erc20_abi,
                                                                          contract_bytecode=self.erc20_contract_code)
        lcc.log_info(
            "ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Get ethereum ERC20 tokens balance in the Ethereum network")
        in_ethereum_erc20_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        in_ethereum_start_erc20_balance = in_ethereum_erc20_balance
        require_that("'in ethereum erc20 contact balance'", in_ethereum_erc20_balance, greater_than(0))

        lcc.set_step("Perform register erc20 token operation")
        bd_result = self.utils.perform_register_erc20_token_operation(self, account=new_account_id,
                                                                      eth_addr=erc20_contract.address,
                                                                      name=token_name, symbol=erc20_symbol,
                                                                      database_api_id=self.__database_api_identifier)
        # todo: uncomment. Bug ECHO-1043
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            "1.20.x"))  # todo: echo_erc20_contract_id

        lcc.set_step("Get created ERC20 token and store ")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        erc20_token_id = result["id"]
        erc20_contract_id = result["contract"]
        lcc.log_info("ERC20 token has id '{}' and contract_id '{}'".format(erc20_token_id, erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_start_erc20_balance))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, in_ethereum_start_erc20_balance)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to {} account completed successfully".format(in_ethereum_start_erc20_balance,
                                                                                     eth_account_address))

        lcc.set_step("Store the first sent operation EthToEcho")
        sidechain_issue_operation = self.echo_ops.get_operation_json("sidechain_issue_operation", example=True)
        sidechain_issue_operations.insert(0, sidechain_issue_operation)
        lcc.log_info("First deposit operation stored")

        lcc.set_step("Get account history operation")
        operation_id = self.echo.config.operation_ids.DEPOSIT_ERC20_TOKEN
        response = self.utils.get_account_history_operations(self, new_account_id, operation_id,
                                                             self.__history_api_identifier,
                                                             limit=len(sidechain_issue_operations))
        lcc.log_info("Account history operations of 'deposit erc20 token' received")
