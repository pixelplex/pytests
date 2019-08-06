# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than, has_length, this_dict, check_that_entry, check_that, \
    is_list, equal_to, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_erc20_account_deposits'"
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

    def get_random_amount(self, _to, _from=1):
        amount = random.randrange(_from, _to)
        if amount == _to:
            return self.get_random_amount(_to=_to, _from=_from)
        return amount

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
            " history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
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
    @lcc.tags("Bug ECHO-1043")
    @lcc.test("Simple work of method 'get_erc20_account_deposits'")
    def method_main_check(self, get_random_string, get_random_valid_asset_name, get_random_valid_account_name):
        new_account_name = get_random_valid_account_name
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name
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
        require_that("'in ethereum erc20 contact balance'", in_ethereum_erc20_balance, greater_than(0))

        lcc.set_step("Perform register erc20 token operation")
        self.utils.perform_register_erc20_token_operation(self, account=new_account_id,
                                                          eth_addr=erc20_contract.address,
                                                          name=token_name, symbol=erc20_symbol,
                                                          database_api_id=self.__database_api_identifier)
        # todo: uncomment. Bug ECHO-1043
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            "1.20.x"))  # todo: echo_erc20_contract_id

        lcc.set_step("First transfer erc20 to ethereum of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_erc20_balance))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[0],
                              log_transaction=False)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[0],
                                                                                       eth_account_address))

        lcc.set_step("First: Get ERC20 account deposits")
        deposits = self.utils.get_erc20_account_deposits(self, new_account_id, self.__database_api_identifier)["result"]
        require_that("'account deposits'", deposits, has_length(len(erc20_deposit_amounts)))
        lcc.log_debug(str(deposits))
        for i, deposit in enumerate(deposits):
            require_that("'account deposit value #'{}''".format(str(i)), deposit["value"],
                         equal_to(str(erc20_deposit_amounts[i])))
            lcc.set_step("Check work of method 'get_erc20_account_deposits', result #'{}'".format(i))
            check_that("'length of erc20 account deposit'", len(deposit), equal_to(7))
            with this_dict(deposits[i]):
                check_that("'deposit erc20 id'", self.validator.is_deposit_erc20_id(deposits[i]["id"]), is_true())
                check_that_entry("account", equal_to(new_account_id))
                check_that_entry("erc20_addr", equal_to(erc20_contract.address[2:]))
                check_that_entry("value", equal_to(str(erc20_deposit_amounts[i])))
                check_that("'transaction_hash'", self.validator.is_hex(deposits[i]["transaction_hash"]), is_true())
                check_that_entry("is_approved", is_true())
                check_that_entry("approves", is_list())

        lcc.set_step("Get updated ethereum ERC20 tokens balance in the Ethereum network")
        in_ethereum_erc20_updated_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        require_that("'in ethereum erc20 contact updated balance'", in_ethereum_erc20_updated_balance,
                     equal_to(in_ethereum_erc20_balance - erc20_deposit_amounts[0]))

        lcc.set_step("Second transfer erc20 to ethereum of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_erc20_updated_balance))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[1],
                              log_transaction=False)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[1],
                                                                                       eth_account_address))

        lcc.set_step("Get final ethereum ERC20 tokens balance in the Ethereum network")
        in_ethereum_erc20_final_balance = self.eth_trx.get_balance_of(erc20_contract, self.eth_account.address)
        require_that("'in ethereum erc20 contact final balance'", in_ethereum_erc20_final_balance,
                     equal_to((in_ethereum_erc20_updated_balance - erc20_deposit_amounts[1])))

        lcc.set_step("Second: Get ERC20 account deposits")
        response = self.utils.get_erc20_account_deposits(self, new_account_id, self.__database_api_identifier)
        deposits = response["result"]
        require_that("'account deposits'", deposits, has_length(len(erc20_deposit_amounts)))
        for i, deposit in enumerate(deposits):
            deposit_value = deposit["value"]
            require_that("'account deposit value #'{}''".format(str(i)), deposit_value,
                         equal_to(str(erc20_deposit_amounts[i])))
            lcc.set_step("Check work of method 'get_erc20_account_deposits', result #'{}'".format(i))
            with this_dict(deposits[i]):
                check_that("'deposit erc20 id'", self.validator.is_deposit_erc20_id(deposits[i]["id"]), is_true())
                check_that_entry("account", equal_to(new_account_id))
                check_that_entry("erc20_addr", equal_to(erc20_contract.address[2:]))
                check_that_entry("value", equal_to(str(erc20_deposit_amounts[i])))
                check_that("'transaction_hash'", self.validator.is_hex(deposits[i]["transaction_hash"]), is_true())
                check_that_entry("is_approved", is_true())
                check_that_entry("approves", is_list())
