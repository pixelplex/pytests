# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, this_dict, check_that_entry, \
    is_str, is_integer

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_erc20_token'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_erc20_token")
@lcc.suite("Check work of method 'get_erc20_token'", rank=1)
class GetERC20Token(BaseTest):

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
        self._connect_to_ganache_ethereum()
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
        self.eth_address = self.web3.eth.accounts[0]
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.tags("Bug ECHO-1043")
    @lcc.test("Simple work of method 'get_erc20_token'")
    def method_main_check(self, get_random_string, get_random_valid_asset_name):
        contract_name = get_random_string
        erc20_symbol = get_random_valid_asset_name

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        deployment = self.eth_trx.deploy_contract_in_ethereum_network(self, eth_account=self.eth_address,
                                                                      contract_abi=self.erc20_abi,
                                                                      contract_bytecode=self.erc20_contract_code)
        eth_erc20_contract_address = deployment.get("contract_address")
        lcc.log_info("ERC20 contract created in Ethereum network, address: '{}'".format(eth_erc20_contract_address))

        lcc.set_step("Perform register erc20 token operation")
        bdt_result = self.utils.perform_register_erc20_token_operation(self, account=self.echo_acc0,
                                                                       eth_addr=eth_erc20_contract_address[2:],
                                                                       name=contract_name,
                                                                       symbol=erc20_symbol,
                                                                       database_api_id=self.__database_api_identifier)
        # todo: uncomment. Bug ECHO-1043
        # echo_erc20_contract_id = self.get_contract_result(bd_result, self.__database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            "1.20.x"))  # todo: echo_erc20_contract_id

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [eth_erc20_contract_address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_erc20_token' with eth_erc20_contract_address='{}' parameter".format(
            eth_erc20_contract_address[2:]))

        lcc.set_step("Check simple work of method 'get_erc20_token'")
        require_that("'length of ERC20 object'", result, has_length(7))

        with this_dict(result):
            if not self.validator.is_erc20_object_id(result["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
            else:
                lcc.log_info("'id' has correct format: erc20_token_object_type")
            # todo: uncomment. Bug ECHO-1043
            # check_that_entry("id", equal_to(echo_erc20_contract_id))
            if not self.validator.is_account_id(result["owner"]):
                lcc.log_error("Wrong format of 'owner', got: {}".format(result["owner"]))
            else:
                lcc.log_info("'owner' has correct format: account_id_object_type")
            if not self.validator.is_eth_address(result["eth_addr"]):
                lcc.log_error("Wrong format of 'eth_addr', got: {}".format(result["eth_addr"]))
            else:
                lcc.log_info("'eth_addr' has correct format: ethereum_address_type")
            if not self.validator.is_contract_id(result["contract"]):
                lcc.log_error("Wrong format of 'contract', got: {}".format(result["contract"]))
            else:
                lcc.log_info("'contract' has correct format: contract_object_type")
            check_that_entry("name", is_str(), quiet=True)
            check_that_entry("symbol", is_str(), quiet=True)
            check_that_entry("decimals", is_integer(), quiet=True)
