# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to
from fixtures.base_fixtures import get_random_integer_up_to_hundred
from common.base_test import BaseTest

SUITE = {
    "description": "Create two accounts, make transfer from 1st account to 2nd account, check 2nd account assert"
}


@lcc.prop("create two accounts", "main")
@lcc.tags("create_two_accounts")
@lcc.suite("Check scenario 'create two accounts'")
class ScenarioOne(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.amount = 1

    def setup_suite(self):
        super().setup_suite()
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

    # @staticmethod
    # def get_valid_account_names(base_name, account_count):
    #     account_names = []
    #     for i in range(account_count):
    #         account_names.append(base_name + str(i))
    #     return account_names

    @lcc.tags("qa")
    @lcc.test("Create two accounts", "main")
    def main(self, get_random_valid_account_name):
        account_count = 2
        account_names = [get_random_valid_account_name + str(i) for i in range(account_count)]
        for account_name in account_names:
            public_key = self.generate_keys()[1]

            lcc.set_step("Create account")
            create_account_operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key,
                                                                                  public_key,
                                                                                  registrar=self.echo_acc0,
                                                                                  signer=self.echo_acc0)

            collected_operation = self.collect_operations(create_account_operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Account is not created")
            operation_result = self.get_operation_results_ids(broadcast_result)
            lcc.log_info("Account is created, id='{}'".format(operation_result))

            lcc.set_step("Check that account with name '{}' made correctly.".format(account_name))
            account_id_from_broadcast_result = broadcast_result["trx"]["operation_results"][0][1]
            response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                            self.__database_api_identifier)
            account_id = self.get_response(response_id)["result"]["id"]
            if account_id != account_id_from_broadcast_result:
                lcc.log_error("Account '{}' is wrong".format(account_id_from_broadcast_result))
            else:
                lcc.log_info("Account '{}' is correct".format(account_id_from_broadcast_result))

            lcc.set_step("Transfer from echo_acc0 to 1st account")
            amount = get_random_integer_up_to_hundred()
            lcc.log_debug(str(amount))
            transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                      from_account_id=self.echo_acc0,
                                                                      to_account_id=account_id,
                                                                      amount=amount, debug_mode=True)
            collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier,
                                                          debug_mode=True)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       debug_mode=True)
            if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
                raise Exception("Account is not created")
            else:
                lcc.log_info("Transfer was done: from {} to {}, amount = {}".format(self.echo_acc0, account_id, amount))


