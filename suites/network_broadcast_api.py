# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, contains_string

from common.base_test import BaseTest

SUITE = {
    "description": "Check all the methods belonging to the network_broadcast_api"
}


@lcc.suite("Testing 'Network broadcast API' methods call")
@lcc.hidden()
class NetworkBroadcastApi(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("network_broadcast")
        lcc.log_info(
            "Network broadcast API identifiers is '{}'".format(self.__api_identifier))

    @lcc.test("Broadcast block")
    @lcc.tags("don't work")
    def test_broadcast_block(self):
        lcc.set_step("Retrieve broadcast block")
        response_id = self.send_request(self.get_request("broadcast_block", [self.get_expected("get_block")]),
                                        self.__api_identifier)
        response = self.get_response(response_id, is_positive=False)

        lcc.set_step("Response")
        check_that(
            "'error message'",
            response["error"]["message"],
            contains_string("unlinkable block: block does not link to known chain")
        )

    @lcc.test("Broadcast transaction")
    @lcc.tags("don't work")
    def test_broadcast_transaction(self):
        lcc.set_step("Retrieve broadcast transaction")
        response_id = self.send_request(
            self.get_request("broadcast_transaction", [self.get_expected("get_transaction")]),
            self.__api_identifier)
        response = self.get_response(response_id, is_positive=False)

        lcc.set_step("Response")
        check_that(
            "'error message'",
            response["error"]["message"],
            contains_string("Assert Exception: trx.ref_block_prefix == tapos_block_summary.block_id._hash[1]: ")
        )

    @lcc.test("Broadcast transaction synchronous")
    @lcc.hidden()
    def test_broadcast_transaction_synchronous(self, trx):
        pass

    @lcc.test("Broadcast transaction with callback")
    @lcc.hidden()
    def test_broadcast_transaction_with_callback(self, callback, trx):
        pass
