# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest
from project import BLOCK_RELEASE_INTERVAL

SUITE = {
    "description": "Smoke testing sidechain. Check the input/output of the ethereum in the network Echo"
}


@lcc.prop("testing", "main")
@lcc.tags("sidechain_smoke_test")
@lcc.hidden()
@lcc.suite("Check scenario 'Sidechain smoke test'")
class SidechainSmokeTest(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.temp_count = 0
        self.block_count = 10
        self.waiting_time_result = 0

    def get_eth_address(self, account_id, timeout=BLOCK_RELEASE_INTERVAL):
        self.temp_count += 1
        response_id = self.send_request(self.get_request("get_eth_address", [account_id]),
                                        self.__database_api_identifier, debug_mode=True)
        response = self.get_response(response_id, log_response=True)
        if response["result"]:
            return response
        if self.temp_count <= self.block_count:
            self.set_timeout_wait(timeout, print_log=False)
            self.waiting_time_result = self.waiting_time_result + timeout
            return self.get_eth_address(account_id, timeout=timeout)
        raise Exception("No ethereum address of '{}' account. "
                        "Waiting time result='{}'".format(account_id, self.waiting_time_result))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("Smoke test of sidechain work")
    def sidechain_smoke_test(self):
        pass
