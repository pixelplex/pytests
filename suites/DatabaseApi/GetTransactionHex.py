# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that, is_true, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_transaction_hex'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_transaction_hex")
@lcc.suite("Check work of method 'get_transaction_hex'", rank=1)
class GetTransaction(BaseTest):

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
    @lcc.test("Simple work of method 'get_transaction_hex'")
    def method_main_check(self):
        lcc.set_step("Collect 'get_transaction_hex' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Broadcast transaction that contains simple transfer operation to the ECHO network")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result, signed_tx, signed_tx_obj = self.echo_ops.broadcast(echo=self.echo,
                                                                             list_operations=collected_operation,
                                                                             log_broadcast=False, get_signed_tx=True)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        lcc.set_step("Calculate hex of signed transaction")
        signed_tx_hex_calculated = bytes(signed_tx_obj).hex()
        lcc.log_info("Calculated hex of signed transaction: '{}'".format(signed_tx_hex_calculated))

        lcc.set_step("Get transaction hex")
        response_id = self.send_request(self.get_request("get_transaction_hex", [signed_tx]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        signed_tx_hex_by_api_method = response["result"]
        lcc.log_info("Hex of signed transaction got by 'get_transaction_hex' api method: '{}'".format(
            signed_tx_hex_by_api_method))

        lcc.set_step("Compare hex strings of signed transaction")
        check_that(
            "hex of signed transaction",
            signed_tx_hex_by_api_method[:-2], equal_to(signed_tx_hex_calculated), quiet=True
        )
