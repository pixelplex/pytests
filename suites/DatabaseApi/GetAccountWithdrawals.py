# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, this_dict, greater_than_or_equal_to, check_that_entry, is_bool, \
    is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_withdrawals'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_account_withdrawals")
@lcc.suite("Check work of method 'get_account_withdrawals'", rank=1)
class GetAccountWithdrawals(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    @staticmethod
    def get_random_amount(_to, _from=0.01):
        return round(random.uniform(_from, _to))

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
    @lcc.test("Simple work of method 'get_account_withdrawals'")
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
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Send eth to ethereum address of created account")
        transaction = self.eth_trx.get_transfer_transaction(web3=self.web3, to=eth_account_address,
                                                            value=eth_amount)
        self.eth_trx.broadcast(web3=self.web3, transaction=transaction)

        lcc.set_step("Get account balance in ethereum")
        ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                           self.eth_asset)["amount"]

        lcc.set_step("First withdraw eth from ECHO network to Ethereum network")
        withdraw_amount_1 = self.get_random_amount(_to=ethereum_balance)
        lcc.log_info("Withdrawing '{}' eeth from '{}' account".format(withdraw_amount_1, new_account))
        self.utils.perform_withdraw_eth_operation_operation(self, new_account, eth_account_address[2:],
                                                            withdraw_amount_1, self.__database_api_identifier)

        lcc.set_step("Get updated account balance in ethereum after first withdraw")
        ethereum_balance = self.utils.get_account_balances(self, new_account, self.__database_api_identifier,
                                                           self.eth_asset)["amount"]

        lcc.set_step("Second withdraw eth from ECHO network to Ethereum network")
        withdraw_amount_2 = self.get_random_amount(_to=ethereum_balance)
        lcc.log_info("Withdrawing '{}' eeth from '{}' account".format(withdraw_amount_2, new_account))
        self.utils.perform_withdraw_eth_operation_operation(self, new_account, eth_account_address[2:],
                                                            withdraw_amount_2, self.__database_api_identifier)

        lcc.set_step("Get deposits of created account")
        params = [new_account]
        response_id = self.send_request(self.get_request("get_account_withdrawals", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_withdrawals' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_account_withdrawals'")
        withdraw = response["result"]
        withdraw_ids = []
        withdraw_values = [withdraw_amount_1, withdraw_amount_2]
        for i in range(len(withdraw)):
            require_that(
                "'first deposit of created account'",
                len(withdraw[i]), is_(7)
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
                check_that_entry("value", is_(withdraw_values[i]), quiet=True)
                # todo: always False, remove false when the bug is fixed
                check_that_entry("is_approved", is_bool(False), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)

        lcc.set_step("Get deposit by id")
        response_id = self.send_request(self.get_request("get_objects", [withdraw_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_objects' with param: {}".format(withdraw_ids))

        lcc.log_info("Compare withdrawals in 'get_account_withdrawals' with method 'get_objects'")
        for i in range(len(withdraw)):
            with this_dict(withdraw[i]):
                check_that_entry("id", is_(response[i]["id"]), quiet=True)
                check_that_entry("withdraw_id", is_(response[i]["withdraw_id"]), quiet=True)
                check_that_entry("account", is_(response[i]["account"]), quiet=True)
                check_that_entry("eth_addr", is_(response[i]["eth_addr"]), quiet=True)
                check_that_entry("value", is_(response[i]["value"]), quiet=True)
                check_that_entry("is_approved", is_(response[i]["is_approved"]), quiet=True)
                check_that_entry("approves", is_(response[i]["approves"]), quiet=True)
