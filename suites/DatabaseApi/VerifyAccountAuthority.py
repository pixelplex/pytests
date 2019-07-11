# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'verify_account_authority'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "verify_account_authority")
@lcc.suite("Check work of method 'verify_account_authority'", rank=1)
class VerifyAccountAuthority(BaseTest):

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
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        lcc.log_info("Registration API identifier is '{}'".format(self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def get_account_active_keys(self, account_id):
        lcc.set_step("Get active keys info about account: {}".format(account_id))
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        account_active_keys = response["result"][0]["active"]

        lcc.log_info("Active keys of account {} were taken".format(account_id))

        return account_active_keys

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'verify_account_authority'")
    def method_main_check(self):
        active_key = self.get_account_active_keys(self.echo_acc0)
        lcc.log_info("{}".format(active_key))
        public_key = active_key["key_auths"][0][0]

        lcc.set_step("Verify authority of '{}' account".format(self.echo_acc0))
        params = [self.echo_acc0, [public_key]]
        response_id = self.send_request(self.get_request("verify_account_authority", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call 'verify_account_authority' with '{}' parameters".format(params))

        require_that(
            "account authority verify status",
            response["result"], is_true()
        )
