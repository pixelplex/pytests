# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, this_dict, check_that_entry, is_str, is_list, is_integer, \
    is_dict, check_that, equal_to, has_length, is_true

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_block")
@lcc.suite("Check work of method 'get_block'", rank=1)
class GetBlock(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_block'")
    def method_main_check(self):
        lcc.set_step("Get the full first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block", [block_num]), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block'")
        block_header = response["result"]
        require_that(
            "'the first full block'",
            block_header, has_length(11)
        )
        with this_dict(block_header):
            check_that_entry("previous", is_str("0000000000000000000000000000000000000000"), quiet=True)
            if not self.validator.is_iso8601(block_header["timestamp"]):
                lcc.log_error("Wrong format of 'timestamp', got: {}".format(block_header["timestamp"]))
            else:
                lcc.log_info("'timestamp' has correct format: iso8601")
            if not self.validator.is_account_id(block_header["account"]):
                lcc.log_error("Wrong format of 'account id', got: {}".format(block_header["account"]))
            else:
                lcc.log_info("'id' has correct format: account_id")
            check_that_entry("transaction_merkle_root", is_str("0000000000000000000000000000000000000000"), quiet=True)
            check_that_entry("vm_root", is_str(), quiet=True)
            check_that_entry("extensions", is_list(), quiet=True)
            check_that_entry("ed_signature", is_str(), quiet=True)
            check_that_entry("round", is_integer(), quiet=True)
            check_that_entry("rand", is_str(), quiet=True)
            check_that_entry("cert", is_dict(), quiet=True)
            check_that_entry("transactions", is_list(), quiet=True)

        certificate = block_header["cert"]
        with this_dict(certificate):
            check_that_entry("_rand", is_str(), quiet=True)
            check_that_entry("_block_hash", is_str(), quiet=True)
            check_that_entry("_producer", is_integer(), quiet=True)
            check_that_entry("_signatures", is_list(), quiet=True)

        signatures = certificate["_signatures"]
        if block_header["account"] == "1.2.0":
            check_that("'_signatures'", signatures, is_list([]), quiet=True)
        else:
            require_that(
                "'_signatures'",
                signatures, has_length(5)
            )
            for i in range(len(signatures)):
                with this_dict(signatures[i]):
                    check_that_entry("_step", is_integer(), quiet=True)
                    check_that_entry("_value", is_integer(), quiet=True)
                    check_that_entry("_signer", is_integer(), quiet=True)
                    check_that_entry("_bba_sign", is_str(), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_block")
@lcc.suite("Positive testing of method 'get_block'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def compare_objects(self, first_field, second_field, key=None):
        if isinstance(first_field, (list, dict)):
            if isinstance(first_field, list) and len(first_field):
                for key, elem in enumerate(first_field):
                    self.compare_objects(elem, second_field[key])
            elif isinstance(first_field, dict) and len(first_field):
                for key in list(first_field.keys()):
                    self.compare_objects(first_field[key], second_field[key], key)
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
    @lcc.test("Broadcast transaction and check info about it in block")
    @lcc.depends_on("DatabaseApi.GetBlock.GetBlock.method_main_check")
    def check_transaction_info_in_block(self):
        lcc.set_step("Collect 'get_transaction' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Broadcast transaction that contains simple transfer operation to the ECHO network")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        lcc.set_step("Get block, that contains transaction")
        broadcast_transaction_block_num = broadcast_result["block_num"]
        response_id = self.send_request(self.get_request("get_block", [broadcast_transaction_block_num]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block' with block_num='{}' parameter".format(broadcast_transaction_block_num))

        lcc.set_step("Compare transaction objects (broadcast_result, 'get_block' method)")
        transaction_from_broadcast_result = broadcast_result["trx"]
        transaction_from_api_method = response["result"]["transactions"][0]

        require_that(
            "'transaction from broadcast result'",
            transaction_from_broadcast_result, has_length(8)
        )
        require_that(
            "'transaction from 'get_block' method result'",
            transaction_from_api_method, has_length(8)
        )
        self.compare_objects(transaction_from_broadcast_result, transaction_from_api_method)
