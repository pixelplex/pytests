# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Create two accounts, perform transfer from 1st account to 2nd account, create asset by 2nd account"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("Scenarios", "create_transfer_asset")
@lcc.suite("Create two accounts")
class CreateTransferAsset(BaseTest):

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("CreateTransferAsset")
    def create_transfer_asset(self, get_random_valid_account_name, get_random_integer, get_random_valid_asset_name):
        account_count, transfer_amount_for_main_account = 2, get_random_integer
        account_names = [get_random_valid_account_name + str(i) for i in range(account_count)]
        created_account_ids, private_keys = [], []
        asset_id = self.echo_asset
        random_symbol_name = get_random_valid_asset_name

        lcc.set_step("Create two accounts")
        for account_name in account_names:
            # keys = self.generate_keys()
            # private_keys.append(keys[0])
            # account_id = self.utils.get_account_id(self, account_names=account_name, account_keys=keys,
            #                                        database_api_id=self.__database_api_identifier,
            #                                        signer=self.echo_acc0)
            account_id = self.get_account_id(account_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
            created_account_ids.append(account_id)
        lcc.log_info("Two accounts created, ids: #1: '{}', #2: '{}'".format(created_account_ids[0],
                                                                            created_account_ids[1]))

        lcc.set_step("Check created accounts by id")
        for i in range(len(account_names)):
            response_account_by_name = self.send_request(self.get_request("get_account_by_name", [account_names[i]]),
                                                         self.__database_api_identifier)
            account_id = self.get_response(response_account_by_name)["result"]["id"]
            check_that("'Created account with id:'{}' was made correctly".format(account_id),
                       account_id, equal_to(created_account_ids[i]))

        lcc.set_step("Get balance of main and first accounts before transfer (from main to first)")
        main_account_balance_before_transfer = self.utils.get_account_balances(self, account=self.echo_acc0,
                                                                               database_api_id=
                                                                               self.__database_api_identifier)
        lcc.log_info(
            "Account '{}' balance = '{}'".format(self.echo_acc0, main_account_balance_before_transfer["amount"]))
        first_account_balance_before_transfer = self.utils.get_account_balances(self, account=created_account_ids[0],
                                                                                database_api_id=
                                                                                self.__database_api_identifier)
        lcc.log_info("Account '{}' balance = '{}'".format(created_account_ids[0],
                                                          first_account_balance_before_transfer["amount"]))

        lcc.set_step("Transfer from main account to first account")
        perform_transfer_operations = self.utils.perform_transfer_operations(self, account_1=self.echo_acc0,
                                                                             account_2=created_account_ids[0],
                                                                             database_api_id=
                                                                             self.__database_api_identifier,
                                                                             transfer_amount=
                                                                             transfer_amount_for_main_account)
        perform_transfer_operation_fee = perform_transfer_operations["trx"]["operations"][0][1]["fee"]["amount"]
        lcc.log_info("Transfer operation performed")

        lcc.set_step("Get balance of main and first accounts after transfer (from main to first)")
        main_account_balance_after_transfer = self.utils.get_account_balances(self, account=self.echo_acc0,
                                                                              database_api_id=
                                                                              self.__database_api_identifier)
        lcc.log_info(
            "Account '{}' balance = '{}'".format(self.echo_acc0, main_account_balance_after_transfer["amount"]))
        first_account_balance__after_transfer = self.utils.get_account_balances(self, account=created_account_ids[0],
                                                                                database_api_id=
                                                                                self.__database_api_identifier)
        lcc.log_info("Account '{}' balance = '{}'".format(created_account_ids[0],
                                                          first_account_balance__after_transfer["amount"]))

        lcc.set_step("Check transfer from main account to first account")
        check_that("'updated balance of main account'", int(main_account_balance_after_transfer["amount"]),
                   equal_to(int(main_account_balance_before_transfer[
                                    "amount"]) - transfer_amount_for_main_account - perform_transfer_operation_fee)
                   )
        check_that("'updated balance of first account'", first_account_balance__after_transfer["amount"],
                   equal_to(int(first_account_balance_before_transfer["amount"]) + transfer_amount_for_main_account)
                   )

        lcc.set_step("Get balance of second account")
        second_account_balance_before_transfer = self.utils.get_account_balances(self, account=created_account_ids[1],
                                                                                 database_api_id=
                                                                                 self.__database_api_identifier)
        lcc.log_info(
            "Account '{}' balance = '{}'".format(created_account_ids[1],
                                                 second_account_balance_before_transfer["amount"]))

        lcc.set_step("Transfer from first account to second account")
        transfer_amount_for_first_account = int(
            first_account_balance__after_transfer["amount"]) - perform_transfer_operation_fee
        perform_transfer_operations = self.utils.perform_transfer_operations(self, account_1=created_account_ids[0],
                                                                             account_2=created_account_ids[1],
                                                                             database_api_id=
                                                                             self.__database_api_identifier,
                                                                             transfer_amount=
                                                                             transfer_amount_for_first_account,
                                                                             log_broadcast=True
                                                                             )
