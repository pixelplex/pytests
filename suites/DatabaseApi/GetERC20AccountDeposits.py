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
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
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
        self.erc20_balanceOf = self.get_byte_code("erc20", "balanceOf(address)", ethereum_contract=True)

    def get_random_amount(self, _to, _from=1):
        amount = random.randrange(_from, _to)
        if amount == _to:
            return self.get_random_amount(_to=_to, _from=_from)
        return amount

    def check_erc20_account_deposits(self, deposits, erc20_deposit_amounts, new_account_id, erc20_contract_address):
        require_that("'account deposits'", deposits, has_length(len(erc20_deposit_amounts)), quiet=True)
        for i, deposit in enumerate(deposits):

            lcc.set_step("Check work of method 'get_erc20_account_deposits', deposit #'{}'".format(i))
            check_that("'length of erc20 account deposit'", deposit, has_length(7), quiet=True)
            with this_dict(deposit):
                if not self.validator.is_deposit_erc20_id(deposit["id"]):
                    lcc.log_error("Wrong format of 'deposit_erc20_id', got: {}".format(deposit["id"]))
                else:
                    lcc.log_info("'deposit_erc20_id' has correct format: {}".format(deposit["id"]))
                check_that_entry("account", equal_to(new_account_id), quiet=True)
                check_that_entry("erc20_addr", equal_to(erc20_contract_address[2:]), quiet=True)
                check_that_entry("value", equal_to(str(erc20_deposit_amounts[i])), quiet=True)
                if not self.validator.is_hex(deposit["transaction_hash"]):
                    lcc.log_error("Wrong format of 'transaction_hash', got: {}".format(deposit["transaction_hash"]))
                else:
                    lcc.log_info("'transaction_hash' has correct format: hex")
                check_that_entry("is_approved", is_true(), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier,
                                                                           ))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_account = self.get_default_ethereum_account()
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_account.address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.tags("Bug ECHO-1141")
    @lcc.disabled()
    @lcc.test("Simple work of method 'get_erc20_account_deposits'")
    def method_main_check(self, get_random_valid_account_name, get_random_string, get_random_valid_asset_name):
        new_account_name = get_random_valid_account_name
        token_name = "erc20" + get_random_string
        erc20_symbol = get_random_valid_asset_name
        erc20_deposit_amounts = []

        lcc.set_step("Create and get new account")
        new_account_id = self.get_account_id(new_account_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account_id))

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account_id, self.__database_api_identifier)
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
        require_that("'in ethereum erc20 contact balance'", in_ethereum_erc20_balance, greater_than(0), quiet=True)

        # todo: uncomment. Bug ECHO-1141
        lcc.set_step("Perform register erc20 token operation")
        broadcast_result = self.utils.perform_sidechain_erc20_register_token_operation(self, account=new_account_id,
                                                                                       eth_addr=erc20_contract.address,
                                                                                       name=token_name,
                                                                                       symbol=erc20_symbol,
                                                                                       database_api_id=self.
                                                                                       __database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            broadcast_result["trx"]["operation_results"][0][1]))

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        erc20_token_id = result["id"]
        erc20_contract_id = result["contract"]
        lcc.log_info("ERC20 token has id '{}' and contract_id '{}'".format(erc20_token_id, erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_erc20_balance))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[0],
                              log_transaction=False)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[0],
                                                                                       eth_account_address))

        lcc.set_step("First: Get ERC20 account deposits")
        deposits = self.utils.get_erc20_account_deposits(self, new_account_id, self.__database_api_identifier)["result"]
        self.check_erc20_account_deposits(deposits, erc20_deposit_amounts, new_account_id,
                                          erc20_contract_address=erc20_contract.address)

        lcc.set_step("Get ethereum ERC20 tokens balance after first transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_first_transfer = self.eth_trx.get_balance_of(erc20_contract,
                                                                                     self.eth_account.address)
        require_that("'in ethereum erc20 contact balance after first transfer'",
                     in_ethereum_erc20_balance_after_first_transfer,
                     equal_to(in_ethereum_erc20_balance - erc20_deposit_amounts[0]), quiet=True)

        lcc.set_step("Second transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=in_ethereum_erc20_balance_after_first_transfer))
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, erc20_deposit_amounts[1],
                              log_transaction=False)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[1],
                                                                                       eth_account_address))

        lcc.set_step("Get ethereum ERC20 tokens balance after second transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_second_transfer = self.eth_trx.get_balance_of(erc20_contract,
                                                                                      self.eth_account.address)
        require_that("'in ethereum erc20 contact balance after second transfer'",
                     in_ethereum_erc20_balance_after_second_transfer,
                     equal_to((in_ethereum_erc20_balance_after_first_transfer - erc20_deposit_amounts[1])), quiet=True)

        lcc.set_step("Second: Get ERC20 account deposits")
        deposits = self.utils.get_erc20_account_deposits(self, new_account_id, self.__database_api_identifier,
                                                         previous_account_deposits=deposits[0])["result"]
        self.check_erc20_account_deposits(deposits, erc20_deposit_amounts, new_account_id,
                                          erc20_contract_address=erc20_contract.address)

        lcc.set_step("Third transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(in_ethereum_erc20_balance_after_second_transfer)
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address,
                              erc20_deposit_amounts[2], log_transaction=False)
        lcc.log_info("Transfer '{}' erc20 tokens to '{}' account completed successfully".format(
            in_ethereum_erc20_balance_after_first_transfer, eth_account_address))

        lcc.set_step("Get ethereum ERC20 tokens balance after final transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_final_transfer = self.eth_trx.get_balance_of(erc20_contract,
                                                                                     self.eth_account.address)
        require_that("'in ethereum erc20 contact balance after final transfer'",
                     in_ethereum_erc20_balance_after_final_transfer, equal_to(0), quiet=True)

        lcc.set_step("Third: Get ERC20 account deposits")
        deposits = self.utils.get_erc20_account_deposits(self, new_account_id, self.__database_api_identifier,
                                                         previous_account_deposits=deposits[1])["result"]
        self.check_erc20_account_deposits(deposits, erc20_deposit_amounts, new_account_id,
                                          erc20_contract_address=erc20_contract.address)

        lcc.set_step("Call method 'balanceOf' ERC20 account of ECHO network")
        argument = self.get_byte_code_param(new_account_id)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(erc20_contract_id))

        lcc.set_step("Get ERC20 account balance of ECHO network")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        in_echo_erc20_balance = self.get_contract_output(contract_result, output_type=int)
        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance, equal_to(in_ethereum_erc20_balance),
                     quiet=True)
