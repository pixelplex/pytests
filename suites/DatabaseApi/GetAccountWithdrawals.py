# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, this_dict, greater_than_or_equal_to, check_that_entry, \
    is_bool, is_list, has_length, check_that, equal_to, starts_with

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_withdrawals'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_withdrawals", "sidechain")
@lcc.suite("Check work of method 'get_account_withdrawals'", rank=1)
class GetAccountWithdrawals(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.eth_address = None
        self.echo_acc0 = None

    @staticmethod
    def get_random_amount(_to, _from=0.01):
        return round(random.uniform(_from, _to))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.eth_address = self.get_default_ethereum_account().address
        lcc.log_info("Ethereum address in the ethereum network: '{}'".format(self.eth_address))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_withdrawals'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        eth_amount = 0.01
        withdraw_ids = []
        withdraw_values = []
        sidechain_burn_operations = []

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

        lcc.set_step("Get unpaid fee for ethereum address creation")
        unpaid_fee_in_ethereum = self.eth_trx.get_unpaid_fee(self, self.web3, new_account)
        lcc.log_info("Unpaid fee for creation ethereum address for '{}' account: '{}'".format(new_account,
                                                                                              unpaid_fee_in_ethereum))

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, _from=self.eth_address,
                                                            _to=eth_account_address,
                                                            value=eth_amount + unpaid_fee_in_ethereum)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier)

        lcc.set_step("First withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=int(ethereum_balance))
        withdraw_values.append(withdraw_amount)
        self.utils.perform_withdraw_eth_operation(self, new_account, self.eth_address, withdraw_amount,
                                                  self.__database_api_identifier)
        lcc.log_info("Withdraw '{}' eeth from '{}' account".format(withdraw_amount, new_account))

        lcc.set_step("Store the first withdraw operation EchoToEth")
        sidechain_burn_operation = self.echo_ops.get_operation_json("sidechain_burn_operation", example=True)
        sidechain_burn_operation[1]["value"].update({"amount": withdraw_values[0]})
        sidechain_burn_operation[1].update({"account": new_account})
        sidechain_burn_operations.insert(0, sidechain_burn_operation)
        lcc.log_info("First withdraw operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_BURN
        response = self.utils.get_account_history_operations(self, new_account, operation_id,
                                                             self.__history_api_identifier,
                                                             limit=len(sidechain_burn_operations))
        lcc.log_info("Account history operations of 'sidechain_burn_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i in range(len(response["result"])):
            operation_in_history = response["result"][i]["op"]
            lcc.set_step("Check operation #{} in account history operations".format(str(i)))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id))
            with this_dict(operation_in_history[1]):
                check_that_entry("fee", equal_to(sidechain_burn_operations[i][1]["fee"]))
                with this_dict(operation_in_history[1]["value"]):
                    self.check_uint256_numbers(operation_in_history[1]["value"], "amount")
                    check_that_entry("asset_id", equal_to(sidechain_burn_operations[i][1]["value"]["asset_id"]))
                check_that_entry("account", equal_to(sidechain_burn_operations[i][1]["account"]))
                check_that_entry("withdraw_id",
                                 starts_with(self.get_object_type(self.echo.config.object_types.WITHDRAW_ETH)))

        lcc.set_step("Get updated account balance in ethereum after first withdraw")
        ethereum_balance = self.utils.get_eth_balance(self, new_account, self.__database_api_identifier,
                                                      previous_balance=ethereum_balance)

        lcc.set_step("Second withdraw eth from ECHO network to Ethereum network")
        withdraw_amount = self.get_random_amount(_to=int(ethereum_balance))
        withdraw_values.append(withdraw_amount)
        self.utils.perform_withdraw_eth_operation(self, new_account, self.eth_address, withdraw_amount,
                                                  self.__database_api_identifier)
        lcc.log_info("Withdraw '{}' eeth from '{}' account".format(withdraw_amount, new_account))

        lcc.set_step("Store the second withdraw operation EchoToEth")
        sidechain_burn_operation = self.echo_ops.get_operation_json("sidechain_burn_operation", example=True)
        sidechain_burn_operation[1]["value"].update({"amount": withdraw_values[1]})
        sidechain_burn_operation[1].update({"account": new_account})
        sidechain_burn_operations.insert(0, sidechain_burn_operation)
        lcc.log_info("Second withdraw operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_BURN
        response = self.utils.get_account_history_operations(self, new_account, operation_id,
                                                             self.__history_api_identifier,
                                                             limit=len(sidechain_burn_operations))
        lcc.log_info("Account history operations of 'sidechain_burn_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i in range(len(response["result"])):
            operation_in_history = response["result"][i]["op"]
            lcc.set_step("Check operation #{} in account history operations".format(str(i)))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id))
            with this_dict(operation_in_history[1]):
                check_that_entry("fee", equal_to(sidechain_burn_operations[i][1]["fee"]))
                with this_dict(operation_in_history[1]["value"]):
                    self.check_uint256_numbers(operation_in_history[1]["value"], "amount")
                    check_that_entry("asset_id", equal_to(sidechain_burn_operations[i][1]["value"]["asset_id"]))
                check_that_entry("account", equal_to(sidechain_burn_operations[i][1]["account"]))
                check_that_entry("withdraw_id",
                                 starts_with(self.get_object_type(self.echo.config.object_types.WITHDRAW_ETH)))

        lcc.set_step("Get withdrawals of created account")
        params = [new_account]
        response_id = self.send_request(self.get_request("get_account_withdrawals", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_withdrawals' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_account_withdrawals'")
        withdraw = response["result"]
        for i in range(len(withdraw)):
            lcc.set_step("Check account withdraw #{}".format(str(i)))
            require_that(
                "'first deposit of created account'",
                withdraw[i], has_length(8)
            )
            with this_dict(withdraw[i]):
                if not self.validator.is_withdraw_eth_id(withdraw[i]["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(withdraw[i]["id"]))
                else:
                    lcc.log_info("'id' has correct format: withdraw_eth_object_type")
                withdraw_ids.append(withdraw[i]["id"])
                check_that_entry("withdraw_id", greater_than_or_equal_to(0), quiet=True)
                check_that_entry("account", is_(new_account), quiet=True)
                if not self.validator.is_eth_address(withdraw[i]["eth_addr"]):
                    lcc.log_error("Wrong format of 'eth_addr', got: {}".format(withdraw[i]["eth_addr"]))
                else:
                    lcc.log_info("'eth_addr' has correct format: ethereum_address_type")
                check_that("value", int(withdraw[i]["value"]), is_(withdraw_values[i]), quiet=True)
                check_that_entry("is_approved", is_bool(True), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)

        lcc.set_step("Get withdraw by id using 'get_objects'")
        response_id = self.send_request(self.get_request("get_objects", [withdraw_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(withdraw_ids))

        lcc.set_step("Compare withdrawals in 'get_account_withdrawals' with method 'get_objects'")
        for i in range(len(withdraw)):
            lcc.set_step("Compare #{}, withdraw in 'get_account_withdrawals' with method 'get_objects'".format(str(i)))
            with this_dict(withdraw[i]):
                check_that_entry("id", is_(response[i]["id"]), quiet=True)
                check_that_entry("withdraw_id", is_(response[i]["withdraw_id"]), quiet=True)
                check_that_entry("account", is_(response[i]["account"]), quiet=True)
                check_that_entry("eth_addr", is_(response[i]["eth_addr"]), quiet=True)
                check_that_entry("value", is_(response[i]["value"]), quiet=True)
                check_that_entry("is_approved", is_(response[i]["is_approved"]), quiet=True)
                check_that_entry("approves", is_(response[i]["approves"]), quiet=True)
                check_that_entry("extensions", is_(response[i]["extensions"]), quiet=True)
