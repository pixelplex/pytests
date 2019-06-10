# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, this_dict, check_that_entry, greater_than, is_integer, is_bool, \
    is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_deposits'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_account_deposits")
@lcc.suite("Check work of method 'get_account_deposits'", rank=1)
class GetAccountsDeposits(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.eth_account_address = None

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
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_deposits'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        eth_amount = 0.01

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        # todo: remove transfer to new account. Bug ECHO-926
        operation = self.echo_ops.get_transfer_operation(self.echo, self.echo_acc0, new_account, amount=200000)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier)

        lcc.set_step("Get ethereum address of created account in the network")
        self.eth_account_address = self.utils.get_eth_address(self, new_account,
                                                              self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, self.eth_account_address))

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=self.eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get deposits of created account")
        params = [new_account]
        response_id = self.send_request(self.get_request("get_account_deposits", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_deposits' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_account_deposits'")
        deposit = response["result"][0]
        require_that(
            "'first deposit of created account'",
            len(deposit), is_(6)
        )
        with this_dict(deposit):
            if not self.validator.is_deposit_eth_id(deposit["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(deposit["id"]))
            else:
                lcc.log_info("'id' has correct format: deposit_eth_object_type")
            check_that_entry("deposit_id", greater_than(0), quiet=True)
            check_that_entry("account", is_(new_account), quiet=True)
            check_that_entry("value", is_integer(), quiet=True)
            check_that_entry("is_approved", is_bool(), quiet=True)
            check_that_entry("approves", is_list(), quiet=False)
