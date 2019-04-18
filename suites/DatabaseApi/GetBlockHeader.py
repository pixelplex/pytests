# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, this_dict, check_that_entry, is_str, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_block_header'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_block_header")
@lcc.suite("Check work of method 'get_block_header'", rank=1)
class GetBlockHeader(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc1))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_block_header'")
    def method_main_check(self):
        lcc.set_step("Get the block header of the first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block_header", [block_num]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call method 'get_block_header' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block_header'")
        block_header = response["result"]
        require_that(
            "'the block header of the first block'",
            len(block_header), is_(6)
        )
        with this_dict(block_header):
            check_that_entry("previous", is_str("0000000000000000000000000000000000000000"), quiet=True)
            if not self.validator.is_iso8601(block_header["timestamp"]):
                lcc.log_error("Wrong format of timestamp, got: {}".format(block_header["timestamp"]))
                check_that_entry("timestamp", is_str(), quiet=True)
            if not self.validator.is_account_id(block_header["account"]):
                lcc.log_error("Wrong format of account id, got: {}".format(block_header["account"]))
                check_that_entry("account", is_str(), quiet=True)
            check_that_entry("transaction_merkle_root", is_str("0000000000000000000000000000000000000000"), quiet=True)
            check_that_entry("vm_root", is_str(), quiet=True)
            check_that_entry("extensions", is_list(), quiet=True)

    @lcc.prop("testing", "positive")
    @lcc.tags("database_api", "get_block_header")
    @lcc.suite("Positive testing of method 'get_block_header'", rank=2)
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
            lcc.log_info(
                "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                               self.__registration_api_identifier))
            self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                                 self.__registration_api_identifier)
            self.echo_acc2 = self.get_account_id(self.echo_acc2, self.__database_api_identifier,
                                                 self.__registration_api_identifier)
            lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc1, self.echo_acc2))

        def teardown_suite(self):
            self._disconnect_to_echopy_lib()
            super().teardown_suite()

        @lcc.prop("type", "method")
        @lcc.test("Check !!!!")
        @lcc.tags("qa")
        # @lcc.depends_on("DatabaseApi.GetBlockHeader.GetBlockHeader.method_main_check")
        def i_do_not_know_name_yet(self):
            lcc.set_step("Perform transfer operation. Store block_header")
            operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc1,
                                                             to_account_id=self.echo_acc2)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            block_header = broadcast_result

            lcc.set_step("Get block header of operation")
