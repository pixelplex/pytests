# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_item, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_references'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_references")
@lcc.suite("Check work of method 'get_account_references'", rank=1)
class GetAccountReferences(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc2 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        lcc.log_info("Registration API identifier is '{}'".format(self.__registration_api_identifier))
        self.echo_acc2 = self.get_account_id(self.accounts[2], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc2))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_references'")
    def method_main_check(self):
        lcc.set_step("Get account references")
        response_id = self.send_request(self.get_request("get_account_references", [self.echo_acc2]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_references' with account_id='{}' parameter".format(self.echo_acc2))

        lcc.set_step("Check 'get_account_references' method result")
        require_that(
            "account references",
            response["result"], is_list([]), quiet=True
        )


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_account_references")
@lcc.suite("Positive testing of method 'get_account_references'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc3 = None
        self.echo_acc4 = None

    def get_account_info(self, account_id):
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"][0]

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        lcc.log_info("Registration API identifier is '{}'".format(self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc3 = self.get_account_id(self.accounts[3], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc4 = self.get_account_id(self.accounts[4], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc3, self.echo_acc4))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Add additional account_auths to account and get references of added account")
    @lcc.depends_on("DatabaseApi.GetAccountReferences.GetAccountReferences.method_main_check")
    def get_references_of_account_that_added_to_another_account_auths(self):
        lcc.set_step("Get account active keys")
        account_info = self.get_account_info(self.echo_acc4)
        account_active_keys = account_info["active"]
        lcc.log_info("Active keys of account {} were taken".format(self.echo_acc4))

        lcc.set_step("Perform account update operation (add account_auths)")
        account_auths = [account_auth[0] for account_auth in account_active_keys["account_auths"]]
        account_auths_new_item = [self.echo_acc3, 1]
        if self.echo_acc3 not in account_auths:
            lcc.log_info("Get required fee for account update operation")
            new_active_keys = account_active_keys.copy()
            new_active_keys["account_auths"].extend([account_auths_new_item])
            account_info["active"] = new_active_keys
            self.utils.perform_account_update_operation(self, self.echo_acc4, account_info,
                                                        self.__database_api_identifier)
        lcc.log_info("'account_auths' of '{}' account was updated".format(self.echo_acc4))

        lcc.set_step("Get updated account active keys")
        account_info = self.get_account_info(self.echo_acc4)
        actual_account_active_keys = account_info["active"]
        require_that(
            "new keys",
            actual_account_active_keys["account_auths"], has_item(account_auths_new_item),
            quiet=True
        )

        lcc.set_step("Get account references")
        response_id = self.send_request(self.get_request("get_account_references", [self.echo_acc3]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_references' with account_id='{}' parameter".format(self.echo_acc3))

        lcc.set_step("Check 'get_account_references' method result")
        require_that(
            "'references of '{}' account'".format(self.echo_acc3),
            response["result"],
            is_list([self.echo_acc4]),
            quiet=True
        )

        # todo: Add test with 'key_auths' updating, BUG ECHO-1031
