# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, this_dict, check_that_entry, greater_than, is_bool, is_list, \
    equal_to, check_that, starts_with, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_deposits'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_deposits", "sidechain")
@lcc.suite("Check work of method 'get_account_deposits'", rank=1)
class GetAccountDeposits(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.eth_address = None

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
    @lcc.test("Simple work of method 'get_account_deposits'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        eth_amount = 0.01
        deposit_ids = []
        deposit_values = []
        sidechain_issue_operations = []

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

        lcc.set_step("First send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, _from=self.eth_address,
                                                            _to=eth_account_address,
                                                            value=eth_amount + unpaid_fee_in_ethereum)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)
        deposit_values.append(self.utils.convert_ethereum_to_eeth(eth_amount))

        lcc.set_step("Store the first sent operation EthToEcho")
        sidechain_issue_operation = self.echo_ops.get_operation_json("sidechain_issue_operation", example=True)
        sidechain_issue_operation[1]["value"].update({"amount": deposit_values[0]})
        sidechain_issue_operation[1].update({"account": new_account})
        sidechain_issue_operations.insert(0, sidechain_issue_operation)
        lcc.log_info("First deposit operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_ISSUE
        response = self.utils.get_account_history_operations(self, new_account, operation_id,
                                                             self.__history_api_identifier,
                                                             limit=len(sidechain_issue_operations))
        lcc.log_info("Account history operations of 'sidechain_issue_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i in range(len(response["result"])):
            operation_in_history = response["result"][i]["op"]
            lcc.set_step("Check operation #{} in account history operations".format(str(i)))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id))
            with this_dict(operation_in_history[1]):
                check_that_entry("fee", equal_to(sidechain_issue_operations[i][1]["fee"]))
                with this_dict(operation_in_history[1]["value"]):
                    self.check_uint256_numbers(operation_in_history[1]["value"], "amount")
                    check_that_entry("asset_id", equal_to(sidechain_issue_operations[i][1]["value"]["asset_id"]))
                check_that_entry("account", equal_to(sidechain_issue_operations[i][1]["account"]))
                check_that_entry("deposit_id",
                                 starts_with(self.get_object_type(self.echo.config.object_types.DEPOSIT_ETH)))

        lcc.set_step("Second send eth to ethereum address of created account")
        eth_amount = eth_amount + eth_amount
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, _from=self.eth_address,
                                                            _to=eth_account_address, value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)
        deposit_values.append(self.utils.convert_ethereum_to_eeth(eth_amount))

        lcc.set_step("Store the second sent operation EthToEcho")
        sidechain_issue_operation = self.echo_ops.get_operation_json("sidechain_issue_operation", example=True)
        sidechain_issue_operation[1]["value"].update({"amount": deposit_values[1]})
        sidechain_issue_operation[1].update({"account": new_account})
        sidechain_issue_operations.insert(0, sidechain_issue_operation)
        lcc.log_info("Second deposit operation stored")

        lcc.set_step("Get account history operations")
        operation_id = self.echo.config.operation_ids.SIDECHAIN_ISSUE
        response = self.utils.get_account_history_operations(self, new_account, operation_id,
                                                             self.__history_api_identifier,
                                                             limit=len(sidechain_issue_operations))
        lcc.log_info("Account history operations of 'sidechain_issue_operation' received")

        lcc.set_step("Check response from method 'get_account_history_operations'")
        for i in range(len(response["result"])):
            operation_in_history = response["result"][i]["op"]
            lcc.set_step("Check operation #{} in account history operations".format(str(i)))
            check_that("operation_id", operation_in_history[0], equal_to(operation_id))
            with this_dict(operation_in_history[1]):
                check_that_entry("fee", equal_to(sidechain_issue_operations[i][1]["fee"]))
                with this_dict(operation_in_history[1]["value"]):
                    self.check_uint256_numbers(operation_in_history[1]["value"], "amount")
                    check_that_entry("asset_id", equal_to(sidechain_issue_operations[i][1]["value"]["asset_id"]))
                check_that_entry("account", equal_to(sidechain_issue_operations[i][1]["account"]))
                check_that_entry("deposit_id",
                                 starts_with(self.get_object_type(self.echo.config.object_types.DEPOSIT_ETH)))

        lcc.set_step("Get deposits of created account")
        params = [new_account]
        response_id = self.send_request(self.get_request("get_account_deposits", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_deposits' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_account_deposits'")
        deposit = response["result"]
        for i in range(len(deposit)):
            lcc.set_step("Check account deposit #{}".format(str(i)))
            require_that(
                "'first deposit of created account'",
                deposit[i], has_length(7)
            )
            with this_dict(deposit[i]):
                if not self.validator.is_deposit_eth_id(deposit[i]["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(deposit[i]["id"]))
                else:
                    lcc.log_info("'id' has correct format: deposit_eth_object_type")
                deposit_ids.append(deposit[i]["id"])
                check_that_entry("deposit_id", greater_than(0), quiet=True)
                check_that_entry("account", is_(new_account), quiet=True)
                check_that("value", int(deposit[i]["value"]), is_(deposit_values[i]), quiet=False)
                check_that_entry("is_approved", is_bool(), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)

        lcc.set_step("Get deposit by id using 'get_objects'")
        response_id = self.send_request(self.get_request("get_objects", [deposit_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(deposit_ids))

        lcc.set_step("Compare deposits in 'get_account_deposits' with method 'get_objects'")
        for i in range(len(deposit)):
            lcc.set_step("Compare #{}, deposit in 'get_account_deposits' with method 'get_objects'".format(str(i)))
            with this_dict(deposit[i]):
                check_that_entry("id", is_(response[i]["id"]), quiet=True)
                check_that_entry("deposit_id", is_(response[i]["deposit_id"]), quiet=True)
                check_that_entry("account", is_(response[i]["account"]), quiet=True)
                check_that_entry("value", is_(response[i]["value"]), quiet=True)
                check_that_entry("is_approved", is_(response[i]["is_approved"]), quiet=True)
                check_that_entry("approves", is_(response[i]["approves"]), quiet=True)
                check_that_entry("extensions", is_(response[i]["extensions"]), quiet=True)
