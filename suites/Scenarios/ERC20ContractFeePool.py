# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Checking ERC20 contract fee pool after creation"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("erc20_contract_fee_pool", "sidechain")
@lcc.suite("Check scenario 'ERC20 contract fee pool'")
class ERC20ContractFeePool(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_address = None
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
        self.eth_address = self.get_default_ethereum_account().address
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario checks ERC20 contract fee pool after creation")
    def erc20_contract_fee_pool_scenario(self, get_random_string, get_random_valid_asset_name, get_random_integer):
        name = "erc20" + get_random_string
        symbol = get_random_valid_asset_name
        registration_erc20_token_operation_id = self.echo.config.operation_ids.REGISTER_ERC20_TOKEN
        register_erc20_token_fee_pool = 0
        amount = get_random_integer

        lcc.set_step("Get fee pool amount in global properties")

        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        response = self.get_response(response_id)
        fee_parameters = response["result"]["parameters"]["current_fees"]["parameters"]
        for fee_parameter in fee_parameters:
            if fee_parameter[0] == registration_erc20_token_operation_id:
                register_erc20_token_fee_pool = fee_parameter[1]["pool_fee"]
        lcc.log_info(
            "Default ERC20 contract fee pool amount after creation is '{}'".format(register_erc20_token_fee_pool))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        erc20_contract = self.eth_trx.deploy_contract_in_ethereum_network(self.web3, eth_address=self.eth_address,
                                                                          contract_abi=self.erc20_abi,
                                                                          contract_bytecode=self.erc20_contract_code)
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(erc20_contract.address))

        lcc.set_step("Perform register erc20 token operation")
        self.utils.perform_register_erc20_token_operation(self, account=self.echo_acc0,
                                                          eth_addr=erc20_contract.address, name=name,
                                                          symbol=symbol, database_api_id=self.__database_api_identifier)

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        erc20_contract_id = self.get_response(response_id)["result"]["contract"]
        lcc.log_info("ERC20 token has contract_id '{}'".format(erc20_contract_id))

        lcc.set_step("Get ERC20 contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [erc20_contract_id]),
                                        self.__database_api_identifier)
        fee_pool_amount = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(erc20_contract_id))

        lcc.set_step("Check ERC20 contract fee pool after creation")
        check_that("'ERC20 contract fee pool balance'", fee_pool_amount, equal_to(register_erc20_token_fee_pool))

        lcc.set_step("Add assets to existed fee pool")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, erc20_contract_id, amount,
                                                        self.__database_api_identifier)
        lcc.log_info("Added '{}' assets value to '{}' contract fee pool successfully".format(amount, erc20_contract_id))

        lcc.set_step("Get updated ERC20 contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [erc20_contract_id]),
                                        self.__database_api_identifier)
        updated_fee_pool_amount_2 = self.get_response(response_id)["result"]["amount"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(erc20_contract_id))

        lcc.set_step("Check ERC20 contract fee pool after replenishment")
        check_that("'updated ERC20 contract fee pool balance'", updated_fee_pool_amount_2,
                   equal_to(fee_pool_amount + amount))
