# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

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
    def test_broadcast_block(self):
        pass

    @lcc.test("Broadcast transaction")
    def test_broadcast_transaction(self):
        pass

    @lcc.test("Broadcast transaction synchronous")
    def test_broadcast_transaction_synchronous(self, trx):
        pass

    @lcc.test("Broadcast transaction with callback")
    def test_broadcast_transaction_with_callback(self, callback, trx):
        pass
