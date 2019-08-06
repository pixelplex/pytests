# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, equal_to, greater_than, has_length, this_dict, require_that_entry, \
    is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Entering the currency ERC20 token in the network ECHO to the account and withdraw that currency"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("sidechain_erc20", "sidechain")
@lcc.suite("Check scenario 'ERC20ToEcho and ERC20FromEchoToEth'")
class ERC20(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.eth_account = None
        self.erc20_contract_code = self.get_byte_code("erc20", "code", ethereum_contract=True)
        self.erc20_abi = self.get_abi("erc20")
        self.erc20_balanceOf = self.get_byte_code("erc20", "balanceOf(address)", ethereum_contract=True)
        self.new_account = None
        self.eth_account_address = None
        self.erc20_contract = None
        self.in_ethereum_erc20_balance = None
        self.in_ethereum_start_erc20_balance = None
        self.in_echo_erc20_balance = None
        self.erc20_token_id = None
        self.erc20_contract_id = None

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

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, self.new_account, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get updated ethereum address of created account in the ECHO network")
        self.eth_account_address = self.utils.get_eth_address(self, self.new_account,
                                                              self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(self.new_account, self.eth_account_address))

        lcc.set_step("Deploy ERC20 contract in the Ethereum network")
        self.erc20_contract = \
            self.eth_trx.deploy_contract_in_ethereum_network(self.web3, eth_address=self.eth_account.address,
                                                             contract_abi=self.erc20_abi,
                                                             contract_bytecode=self.erc20_contract_code)
        lcc.log_info(
            "ERC20 contract created in Ethereum network, address: '{}'".format(self.erc20_contract.address))

        lcc.set_step("Get ethereum account ERC20 tokens balance in the Ethereum network")
        self.in_ethereum_erc20_balance = self.eth_trx.get_balance_of(self.erc20_contract, self.eth_account.address)
        self.in_ethereum_start_erc20_balance = self.in_ethereum_erc20_balance
        require_that("'in ethereum owner's erc20 balance'", self.in_ethereum_erc20_balance, greater_than(0))

        lcc.set_step("Perform register erc20 token operation")
        bd_result = self.utils.perform_register_erc20_token_operation(self, account=self.new_account,
                                                                      eth_addr=self.erc20_contract.address,
                                                                      name=name, symbol=symbol,
                                                                      database_api_id=self.__database_api_identifier)
        # todo: uncomment. Bug ECHO-1043
        # echo_erc20_contract_id = self.get_contract_result(bd_result, self.__database_api_identifier)
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            "1.20.x"))  # todo: echo_erc20_contract_id

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [self.erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        self.erc20_token_id = result["id"]
        self.erc20_contract_id = result["contract"]
        lcc.log_info("ERC20 token has id '{}' and contract_id '{}'".format(self.erc20_token_id, self.erc20_contract_id))

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario entering erc20 tokens to the echo account")
    @lcc.depends_on("SideChain.ERC20.ERC20.erc20_sidechain_pre_run_scenario")
    def erc20_in_scenario(self):
        erc20_deposit_amounts = []

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=self.in_ethereum_erc20_balance))
        self.eth_trx.transfer(self.web3, self.erc20_contract, self.eth_account_address, erc20_deposit_amounts[0])
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[0],
                                                                                       self.eth_account_address))

        lcc.set_step("First: Get ERC20 account deposits")
        response = self.utils.get_erc20_account_deposits(self, self.new_account, self.__database_api_identifier)
        deposits = response["result"]
        require_that("'account deposits'", deposits, has_length(1))
        for i, deposit in enumerate(deposits):
            deposit_value = deposit["value"]
            require_that("'account deposit value #'{}''".format(str(i)), deposit_value,
                         equal_to(str(erc20_deposit_amounts[i])))

        lcc.set_step("Call method 'balanceOf' with account that receive erc20 tokens in the ECHO network")
        argument = self.get_byte_code_param(self.new_account)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=self.erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(self.erc20_contract_id))

        lcc.set_step("Get method 'balanceOf' result")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        in_echo_erc20_balance = self.get_contract_output(contract_result, output_type=int)
        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance, equal_to(erc20_deposit_amounts[0]))

        lcc.set_step("Get updated ethereum account ERC20 tokens balance in the Ethereum network")
        updated_in_ethereum_erc20_balance = self.eth_trx.get_balance_of(self.erc20_contract, self.eth_account.address)
        require_that("'in ethereum owner's erc20 balance'", updated_in_ethereum_erc20_balance,
                     equal_to(self.in_ethereum_erc20_balance - erc20_deposit_amounts[0]))

        lcc.set_step("Second transfer erc20 to ethereum address of created account")
        erc20_deposit_amounts.append(self.get_random_amount(_to=updated_in_ethereum_erc20_balance))
        self.eth_trx.transfer(self.web3, self.erc20_contract, self.eth_account_address, erc20_deposit_amounts[1])
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(erc20_deposit_amounts[1],
                                                                                       self.eth_account_address))

        lcc.set_step("Second: Get ERC20 account deposits")
        response = self.utils.get_erc20_account_deposits(self, self.new_account, self.__database_api_identifier,
                                                         previous_account_deposits=deposits)
        deposits = response["result"]
        require_that("'account deposits'", deposits, has_length(2))
        for i, deposit in enumerate(deposits):
            deposit_value = deposit["value"]
            require_that("'account deposit value #'{}''".format(str(i)), deposit_value,
                         equal_to(str(erc20_deposit_amounts[i])))

        lcc.set_step("Call method 'balanceOf' with account that receive erc20 tokens in the ECHO network")
        argument = self.get_byte_code_param(self.new_account)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=self.erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(self.erc20_contract_id))

        lcc.set_step("Get method 'balanceOf' result")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        in_echo_erc20_balance = self.get_contract_output(contract_result, output_type=int)
        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance,
                     equal_to(erc20_deposit_amounts[0] + erc20_deposit_amounts[1]))

        lcc.set_step("Get final ethereum account ERC20 tokens balance in the Ethereum network")
        final_in_ethereum_erc20_balance = self.eth_trx.get_balance_of(self.erc20_contract, self.eth_account.address)
        require_that("'in ethereum owner'serc20 balance'", final_in_ethereum_erc20_balance,
                     equal_to(updated_in_ethereum_erc20_balance - erc20_deposit_amounts[1]))
        self.in_echo_erc20_balance = in_echo_erc20_balance
        self.in_ethereum_erc20_balance = final_in_ethereum_erc20_balance

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario withdrawing erc20 tokens from the echo account")
    @lcc.depends_on("SideChain.ERC20.ERC20.erc20_in_scenario")
    def erc20_out_scenario(self):
        erc20_withdraw_amounts = []
        withdraw_erc20_token_ids = []

        lcc.set_step("Get ERC20 balance in the ECHO network")
        if self.in_echo_erc20_balance <= 0:
            raise Exception("No ERC20 balance to withdraw")
        lcc.log_info("ERC20 balance in ECHO network: '{}'".format(self.in_echo_erc20_balance))
        lcc.log_info("ERC20 balance in Ethereum network: '{}'".format(self.in_ethereum_erc20_balance))

        lcc.set_step("Perform first withdraw ERC20 token operation")
        erc20_withdraw_amounts.append(str(self.get_random_amount(_to=self.in_echo_erc20_balance)))
        bd_result = self.utils.perform_withdraw_erc20_token_operation(self, account=self.new_account,
                                                                      to=self.eth_account.address,
                                                                      erc20_token=self.erc20_token_id,
                                                                      value=erc20_withdraw_amounts[0],
                                                                      database_api_id=self.__database_api_identifier)
        withdraw_erc20_token_ids.append(self.get_operation_results_ids(bd_result))
        lcc.log_info("Withdraw ERC20 token completed successfully, Withdraw ERC20 token object is '{}'".format(
            withdraw_erc20_token_ids[0]))

        lcc.set_step("Get ERC20 account withdrawals")
        response = self.utils.get_erc20_account_withdrawals(self, self.new_account, self.__database_api_identifier)
        withdrawals = response["result"]
        require_that("'account withdrawals'", withdrawals, has_length(1))
        for i, withdraw in enumerate(withdrawals):
            lcc.log_info("Check account withdraw #'{}'".format(str(i)))
            with this_dict(withdraw):
                require_that_entry("id", equal_to(withdraw_erc20_token_ids[i]))
                require_that_entry("value", equal_to(str(erc20_withdraw_amounts[i])))

        lcc.set_step("Call method 'balanceOf' with account that withdraw erc20 tokens out of ECHO network")
        argument = self.get_byte_code_param(self.new_account)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=self.erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(self.erc20_contract_id))

        lcc.set_step("Get method 'balanceOf' result")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        in_echo_erc20_balance = self.get_contract_output(contract_result, output_type=int)
        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance,
                     equal_to(self.in_echo_erc20_balance - int(erc20_withdraw_amounts[0])))

        lcc.set_step("Get updated ethereum account ERC20 tokens balance in the Ethereum network")
        updated_in_ethereum_erc20_balance = \
            self.utils.get_updated_account_erc20_balance_in_eth_network(self, self.erc20_contract,
                                                                        self.eth_account.address,
                                                                        self.in_ethereum_erc20_balance)
        require_that("'in ethereum owner'serc20 balance'", updated_in_ethereum_erc20_balance,
                     equal_to(self.in_ethereum_erc20_balance + int(erc20_withdraw_amounts[0])))

        lcc.set_step("Perform second withdraw ERC20 token operation to withdraw all ERC20 balance")
        erc20_withdraw_amounts.append(str(in_echo_erc20_balance))
        bd_result = self.utils.perform_withdraw_erc20_token_operation(self, account=self.new_account,
                                                                      to=self.eth_account.address,
                                                                      erc20_token=self.erc20_token_id,
                                                                      value=erc20_withdraw_amounts[1],
                                                                      database_api_id=self.__database_api_identifier)
        withdraw_erc20_token_ids.append(self.get_operation_results_ids(bd_result))
        lcc.log_info("Withdraw ERC20 token completed successfully, Withdraw ERC20 token object is '{}'".format(
            withdraw_erc20_token_ids[1]))

        lcc.set_step("Get ERC20 account withdrawals")
        response = self.utils.get_erc20_account_withdrawals(self, self.new_account, self.__database_api_identifier)
        withdrawals = response["result"]
        require_that("'account withdrawals'", withdrawals, has_length(2))
        for i, withdraw in enumerate(withdrawals):
            lcc.log_info("Check account withdraw #'{}'".format(str(i)))
            with this_dict(withdraw):
                require_that_entry("id", equal_to(withdraw_erc20_token_ids[i]))
                require_that_entry("value", equal_to(str(erc20_withdraw_amounts[i])))

        lcc.set_step("Call method 'balanceOf' with account that withdraw all erc20 tokens out of ECHO network")
        argument = self.get_byte_code_param(self.new_account)
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=self.erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(self.erc20_contract_id))

        lcc.set_step("Get method 'balanceOf' result")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        updated_in_echo_erc20_balance = self.get_contract_output(contract_result, output_type=int)
        require_that("'in echo account's erc20 balance'", updated_in_echo_erc20_balance,
                     equal_to(in_echo_erc20_balance - int(erc20_withdraw_amounts[1])))

        lcc.set_step("Get final ethereum account ERC20 tokens balance in the Ethereum network")
        final_in_ethereum_erc20_balance = \
            self.utils.get_updated_account_erc20_balance_in_eth_network(self, self.erc20_contract,
                                                                        self.eth_account.address,
                                                                        self.in_ethereum_erc20_balance)
        require_that("'in ethereum owner'serc20 balance'", final_in_ethereum_erc20_balance,
                     equal_to(updated_in_ethereum_erc20_balance + int(erc20_withdraw_amounts[1])))
        require_that("'final balance equal to start balance'",
                     final_in_ethereum_erc20_balance == self.in_ethereum_start_erc20_balance, is_true())
