# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_true, has_item, equal_to

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


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "verify_account_authority")
@lcc.suite("Positive testing of method 'verify_account_authority'", rank=2)
class PositiveTesting(BaseTest):
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
        self.echo_acc3 = self.get_account_id(self.echo_acc3, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc4 = self.get_account_id(self.echo_acc4, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0,
                                                                           self.echo_acc3,
                                                                           self.echo_acc4))

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
    @lcc.test("Add additional account_auths to account and verify account authority for it")
    @lcc.depends_on("DatabaseApi.VerifyAccountAuthority.VerifyAccountAuthority.method_main_check")
    def get_potential_signatures_of_accounts_with_additional_account_auths(self):
        first_account_active_keys = self.get_account_active_keys(self.echo_acc3)
        second_account_active_keys = self.get_account_active_keys(self.echo_acc4)
        account_auths = [account_auth[0] for account_auth in second_account_active_keys["account_auths"]]
        account_auths_new_item = [self.echo_acc3, 1]
        lcc.set_step("Update info of {} account (add account_auths)".format(self.echo_acc4))
        if self.echo_acc3 not in account_auths:
            new_active_keys = second_account_active_keys.copy()
            new_active_keys["account_auths"].extend([account_auths_new_item])

            transfer_operation = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                from_account_id=self.echo_acc0,
                to_account_id=self.echo_acc4,
                amount=3000000
            )
            collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            require_that(
                "transfer to created account complete successfully",
                self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
            )

            operation = self.echo_ops.get_account_update_operation(
                echo=self.echo, account=self.echo_acc4,
                key_auths=new_active_keys["key_auths"],
                account_auths=new_active_keys["account_auths"],
                weight_threshold=new_active_keys["weight_threshold"]
            )
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)

            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            require_that(
                "update of created account complete successfully",
                self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
            )

        lcc.log_info("'account_auths' of {} account was updated".format(self.echo_acc4))

        actual_second_account_active_keys = self.get_account_active_keys(self.echo_acc4)
        require_that(
            "new keys",
            actual_second_account_active_keys["account_auths"], has_item(account_auths_new_item),
            quiet=True
        )

        public_key = first_account_active_keys["key_auths"][0][0]

        lcc.set_step("Verify authority of '{}' account".format(self.echo_acc0))
        params = [self.echo_acc4, [public_key]]
        response_id = self.send_request(self.get_request("verify_account_authority", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call 'verify_account_authority' with '{}' parameters".format(params))

        require_that(
            "account authority verify status",
            response["result"], is_true()
        )
        # todo: Wait for bug fix - ECHO-1024
        # todo: Add test with 'key_auths' update, BUG ECHO-1031
