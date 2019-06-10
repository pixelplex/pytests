# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, this_dict, check_that_entry, is_str, is_list, is_integer

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

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_block_header'")
    def method_main_check(self):
        lcc.set_step("Get the block header of the first block in the chain")
        block_num = 1
        response_id = self.send_request(self.get_request("get_block_header", [block_num]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_block_header' with block_num='{}' parameter".format(block_num))

        lcc.set_step("Check simple work of method 'get_block_header'")
        block_header = response["result"]
        require_that(
            "'the block header of the first block'",
            len(block_header), is_(7)
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
            check_that_entry("round", is_integer(), quiet=True)
            check_that_entry("extensions", is_list(), quiet=True)
