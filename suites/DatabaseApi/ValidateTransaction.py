# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that, equal_to, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'validate_transaction'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "validate_transaction")
@lcc.suite("Check work of method 'validate_transaction'", rank=1)
class ValidateTransaction(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    @staticmethod
    def compare_objects(first_field, second_field, key=None):
        if isinstance(first_field, (list, dict)):
            if isinstance(first_field, list) and len(first_field):
                for key, elem in enumerate(first_field):
                    ValidateTransaction.compare_objects(elem, second_field[key])
            elif isinstance(first_field, dict) and len(first_field):
                for key in first_field.keys():
                    ValidateTransaction.compare_objects(first_field[key], second_field[key], key)
        else:
            description = "list element"
            if key:
                description = "'{}'".format(key)
            check_that("{}".format(description), first_field, equal_to(second_field), quiet=True)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'validate_transaction'")
    def method_main_check(self):
        lcc.set_step("Collect 'validate_transaction' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Sign transaction that contains simple transfer operation")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_transaction = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                     no_broadcast=True).json()
        lcc.log_info("Signed transaction: {}".format(signed_transaction))

        lcc.set_step("Validate signed transaction")
        response_id = self.send_request(self.get_request("validate_transaction", [signed_transaction]),
                                        self.__database_api_identifier)
        validate_transaction = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'validate_transaction'")

        lcc.set_step("Compare localy signed and validated transactions")
        require_that(
            "'transaction from 'validate_transaction' result'",
            validate_transaction, has_length(8)
        )
        self.compare_objects(signed_transaction, validate_transaction)
