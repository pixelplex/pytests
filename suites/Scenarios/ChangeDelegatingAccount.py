# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, not_equal_to, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Change delegating account using 'account_update_operation'"
}


@lcc.prop("testing", "main")
@lcc.tags("change_delegating_account")
@lcc.suite("Check scenario 'Change delegating account'")
class ChangeDelegatingAccount(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
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

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes ability to delete or change delegating account.")
    def change_delegating_account_scenario(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Registration an account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get info about account and store current 'delegating_account'")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        current_delegating_account = response["result"][0]["options"]["delegating_account"]
        lcc.log_info("Current delegating account of '{}' is '{}'".format(new_account, current_delegating_account))

        lcc.set_step("Add assets to a new account to pay a fee")
        operation = [
            6,
            {
                "fee": {
                    "amount": 0,
                    "asset_id": "1.3.0"
                },
                "account": new_account,
                "new_options": {
                    "memo_key": response["result"][0]["options"]["memo_key"],
                    "voting_account": response["result"][0]["options"]["voting_account"],
                    "delegating_account": self.echo_acc0,
                    "num_committee": response["result"][0]["options"]["num_committee"],
                    "votes": response["result"][0]["options"]["votes"],
                },
            }
            ,
            new_account]
        fee = self.get_required_fee(operation, self.__database_api_identifier)[0].get("amount")
        self.utils.fill_account_history_with_transfer_operations(self, self.echo, self.echo_acc0, new_account,
                                                                 self.__database_api_identifier,
                                                                 transfer_amount=fee)
        operation[1].get("fee").update({"amount": fee})

        lcc.set_step("Perform 'account_update_operation' to change delegating_account")
        self.echo_ops.broadcast(echo=self.echo, list_operations=operation, debug_mode=True)

        lcc.set_step("Get info about account and store new 'delegating_account'")
        response_id = self.send_request(self.get_request("get_accounts", [[new_account]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        new_delegating_account = response["result"][0]["options"]["delegating_account"]
        lcc.log_info("New delegating account of '{}' is '{}'".format(new_account, new_delegating_account))

        lcc.set_step("Check that 'delegating_account' is updated")
        check_that(
            "new 'delegating_account'",
            new_delegating_account, not_equal_to(current_delegating_account)
        )

        check_that(
            "new 'delegating_account'",
            new_delegating_account, equal_to(self.echo_acc0)
        )
