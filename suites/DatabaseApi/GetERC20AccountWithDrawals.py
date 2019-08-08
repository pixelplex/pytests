# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, greater_than, equal_to, has_length, this_dict, is_true, is_list, \
    check_that_entry, check_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_erc20_account_withdrawals'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("database_api", "get_erc20_account_withdrawals", "sidechain")
@lcc.suite("Check work of method 'get_erc20_account_withdrawals'", rank=1)
class GetERC20AccountWithdrawals(BaseTest):

    def __init__(self):
        super().__init__()
        self.__history_api_identifier = None
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
        erc20_withdrawal_amounts = []
        withdrawal_erc20_token_ids = []

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

        lcc.set_step("Perform register erc20 token operation")
        self.utils.perform_sidechain_erc20_register_token_operation(self, account=new_account_id,
                                                                    eth_addr=erc20_contract.address,
                                                                    name=token_name, symbol=erc20_symbol,
                                                                    database_api_id=self.__database_api_identifier)
        # todo: uncomment. Bug ECHO-1043
        lcc.log_info("Registration of ERC20 token completed successfully, ERC20 token object is '{}'".format(
            "1.20.x"))  # todo: echo_erc20_contract_id

        lcc.set_step("Get created ERC20 token and store contract id in the ECHO network")
        response_id = self.send_request(self.get_request("get_erc20_token", [erc20_contract.address[2:]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        erc20_token_id = result["id"]
        erc20_contract_id = result["contract"]
        lcc.log_info("ERC20 token has id '{}' and contract_id '{}'".format(erc20_token_id, erc20_contract_id))

        lcc.set_step("First transfer erc20 to ethereum address of created account")
        self.eth_trx.transfer(self.web3, erc20_contract, eth_account_address, in_ethereum_erc20_balance,
                              log_transaction=False)
        lcc.log_info(
            "Transfer '{}' erc20 tokens to '{}' account completed successfully".format(in_ethereum_erc20_balance,
                                                                                       eth_account_address))

        lcc.set_step("Get ethereum ERC20 tokens balance after transfer in the Ethereum network")
        in_ethereum_erc20_balance_after_transfer = self.eth_trx.get_balance_of(erc20_contract,
                                                                               self.eth_account.address)
        require_that("'in ethereum erc20 contact balance after transfer'",
                     in_ethereum_erc20_balance_after_transfer, equal_to(0), quiet=True)

        lcc.set_step("Get ERC20 account deposit")
        self.utils.get_erc20_account_deposits(self, new_account_id, self.__database_api_identifier)

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

        lcc.set_step("Perform first withdrawal ERC20 token operation")
        erc20_withdrawal_amounts.append(str(self.get_random_amount(_to=in_echo_erc20_balance)))
        bd_result = self.utils.perform_sidechain_erc20_withdraw_token_operation(self, account=new_account_id,
                                                                                to=self.eth_account.address,
                                                                                erc20_token=erc20_token_id,
                                                                                value=erc20_withdrawal_amounts[0],
                                                                                database_api_id=self.
                                                                                __database_api_identifier)
        withdrawal_erc20_token_ids.append(self.get_operation_results_ids(bd_result))
        lcc.log_info("withdrawal ERC20 token completed successfully, withdrawal ERC20 token object is '{}'".format(
            withdrawal_erc20_token_ids[0]))

        lcc.set_step("First: Get ERC20 account withdrawals")
        withdrawals = self.utils.get_erc20_account_withdrawals(self, new_account_id, self.__database_api_identifier)[
            "result"]
        require_that("'account withdrawals'", withdrawals, has_length(len(erc20_withdrawal_amounts)), quiet=True)
        for i, withdrawal in enumerate(withdrawals):
            lcc.log_info("Check account withdrawal #'{}'".format(i))
            with this_dict(withdrawal):
                check_that_entry("id", equal_to(withdrawal_erc20_token_ids[i]), quiet=True)
                check_that_entry("account", equal_to(new_account_id), quiet=True)
                if not self.validator.is_hex(withdrawals[i]["to"]):
                    lcc.log_error("Wrong format of 'to', got: {}".format(withdrawals[i]["to"]))
                else:
                    lcc.log_info("'erc20_token' has correct format: hex")
                if not self.validator.is_erc20_object_id(withdrawals[i]["erc20_token"]):
                    lcc.log_error("Wrong format of 'erc20_token', got: {}".format(withdrawals[i]["to"]))
                else:
                    lcc.log_info("'erc20_token' has correct format: hex")
                check_that_entry("value", equal_to(str(erc20_withdrawal_amounts[i])), quiet=True)
                check_that_entry("is_approved", is_true(), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)

        lcc.set_step("Call method 'balanceOf' ERC20 account of ECHO network")
        argument = self.get_byte_code_param(new_account_id)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(erc20_contract_id))

        lcc.set_step("Get ERC20 account balance after first withdrawal of  ECHO network")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        in_echo_erc20_balance_after_first_withdrawal = self.get_contract_output(contract_result, output_type=int)
        require_that("'in echo account's erc20 balance'", in_echo_erc20_balance_after_first_withdrawal,
                     equal_to(in_ethereum_erc20_balance - int(erc20_withdrawal_amounts[0])),
                     quiet=True)

        lcc.set_step("Get ethereum ERC20 tokens balance after first withdrawal in the Ethereum network")
        in_ethereum_erc20_balance_after_first_withdraw = self.eth_trx.get_balance_of(erc20_contract,
                                                                                     self.eth_account.address)
        require_that("'in ethereum erc20 contact balance'",
                     str(in_ethereum_erc20_balance_after_first_withdraw), equal_to(erc20_withdrawal_amounts[0]),
                     quiet=True)

        lcc.set_step("Perform second withdrawal ERC20 token operation")
        erc20_withdrawal_amounts.append(str(in_echo_erc20_balance_after_first_withdrawal))
        bd_result = self.utils.perform_sidechain_erc20_withdraw_token_operation(self, account=new_account_id,
                                                                                to=self.eth_account.address,
                                                                                erc20_token=erc20_token_id,
                                                                                value=erc20_withdrawal_amounts[1],
                                                                                database_api_id=self.
                                                                                __database_api_identifier)
        withdrawal_erc20_token_ids.append(self.get_operation_results_ids(bd_result))
        lcc.log_info("withdrawal ERC20 token completed successfully, withdrawal ERC20 token object is '{}'".format(
            withdrawal_erc20_token_ids[0]))

        lcc.set_step("Second: Get ERC20 account withdrawals")
        withdrawals = self.utils.get_erc20_account_withdrawals(self, new_account_id, self.__database_api_identifier)[
            "result"]
        require_that("'account withdrawals'", withdrawals, has_length(len(erc20_withdrawal_amounts)), quiet=True)
        for i, withdrawal in enumerate(withdrawals):
            lcc.log_info("Check account withdrawal #'{}'".format(i))
            with this_dict(withdrawal):
                check_that_entry("id", equal_to(withdrawal_erc20_token_ids[i]), quiet=True)
                check_that_entry("account", equal_to(new_account_id), quiet=True)
                if not self.validator.is_hex(withdrawals[i]["to"]):
                    lcc.log_error("Wrong format of 'to', got: {}".format(withdrawals[i]["to"]))
                else:
                    lcc.log_info("'erc20_token' has correct format: hex")
                if not self.validator.is_erc20_object_id(withdrawals[i]["erc20_token"]):
                    lcc.log_error("Wrong format of 'erc20_token', got: {}".format(withdrawals[i]["to"]))
                else:
                    lcc.log_info("'erc20_token' has correct format: hex")
                check_that_entry("value", equal_to(str(erc20_withdrawal_amounts[i])), quiet=True)
                check_that_entry("is_approved", is_true(), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)

        lcc.set_step("Call method 'balanceOf' ERC20 account of ECHO network")
        argument = self.get_byte_code_param(new_account_id)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.erc20_balanceOf + argument,
                                                              callee=erc20_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Call method 'balanceOf' '{}' contract completed successfully".format(erc20_contract_id))

        lcc.set_step("Get ERC20 account balance after second withdrawal of ECHO network")
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        in_echo_erc20_balance_after_second_withdrawal = self.get_contract_output(contract_result, output_type=int)
        check_that("'in echo account's erc20 balance'", in_echo_erc20_balance_after_second_withdrawal, equal_to(0))

        lcc.set_step("Get ethereum ERC20 tokens balance after second withdrawal in the Ethereum network")
        in_ethereum_erc20_balance_after_second_withdrawal = self.eth_trx.get_balance_of(erc20_contract,
                                                                                        self.eth_account.address)
        require_that("'in ethereum erc20 contact balance'", in_ethereum_erc20_balance_after_second_withdrawal,
                     equal_to(in_echo_erc20_balance), quiet=False)
