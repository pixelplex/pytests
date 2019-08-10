# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_true, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'verify_authority'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "verify_authority")
@lcc.suite("Check work of method 'verify_authority'", rank=1)
class VerifyAuthority(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'verify_authority'")
    def method_main_check(self):
        lcc.set_step("Collect 'verify_authority' valid operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Sign valid transaction")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        transaction_object = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                     no_broadcast=True)
        lcc.log_info("Valid transaction was signed")

        lcc.set_step("Verify authority")
        response_id = self.send_request(self.get_request("verify_authority", [transaction_object]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        require_that(
            'transaction verify status',
            response["result"], is_true()
        )


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "verify_authority")
@lcc.suite("Negative testing of method 'verify_authority'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.signed_transaction_object = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def get_random_private_key(self):
        return self.echo.brain_key().get_private_key_base58()

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Call method with incorrect signed transaction")
    @lcc.depends_on("DatabaseApi.VerifyAuthority.VerifyAuthority.method_main_check")
    def call_method_with_incorrect_signed_transaction(self):
        lcc.set_step("Collect 'verify_authority' non-valid operation")
        signer = self.get_random_private_key()
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1,
                                                                  signer=signer)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Sign non-valid transaction")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.signed_transaction_object = self.echo_ops.broadcast(echo=self.echo,
                                                                 list_operations=collected_operation,
                                                                 no_broadcast=True)
        lcc.log_info("Non-valid transaction was signed")

        lcc.set_step("Verify authority with incorrect signed transaction")
        response_id = self.send_request(self.get_request("verify_authority",
                                                         [self.signed_transaction_object]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        require_that(
            "'verify_authority' return error message",
            response, has_entry("error"), quiet=True,
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with transaction without signature")
    @lcc.depends_on("DatabaseApi.VerifyAuthority.VerifyAuthority.method_main_check")
    def call_method_with_transaction_without_signature(self):
        lcc.set_step("Collect 'verify_authority' non-valid operation")
        signer = self.get_random_private_key()
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1,
                                                                  signer=signer)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Sign non-valid transaction")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        self.signed_transaction_object = self.echo_ops.broadcast(echo=self.echo,
                                                                 list_operations=collected_operation,
                                                                 no_broadcast=True)
        lcc.log_info("Non-valid transaction was signed")

        lcc.set_step("Verify authority of transaction without signature")
        transaction_object = self.signed_transaction_object.copy()
        del transaction_object["signatures"]
        response_id = self.send_request(self.get_request("verify_authority", [transaction_object]),
                                        self.__database_api_identifier)

        response = self.get_response(response_id, negative=True)
        require_that(
            "'verify_authority' return error message",
            response, has_entry("error"), quiet=True,
        )
