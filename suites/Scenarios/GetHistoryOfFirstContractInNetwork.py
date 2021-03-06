# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_not_none

from common.base_test import BaseTest

SUITE = {
    "description": "Testing the receipt of the history of the very first contract in the network"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("get_first_contract_history")
@lcc.suite("Check scenario 'Get history of the first contract in the network'")
class GetHistoryOfFirstContractInNetwork(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.contract_id = "1.14.0"

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("Check contract history of the first contract in the network")
    @lcc.disabled()
    @lcc.tags("Bug ECHO-1036", "Bug ECHO-1037")
    def get_history_of_first_contract_scenario(self):
        stop = start = "1.10.0"
        # todo: change limit to 100. Bug ECHO-1037
        limit = 1

        lcc.set_step("Check that '1.14.0' contract in the network or not")
        response_id = self.send_request(self.get_request("get_objects", [["1.14.0"]]), self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"] == [None]:
            lcc.set_step("Perform create contract operation")
            self.contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                          self.__database_api_identifier)
        elif "error" in response:
            lcc.log_error("'get_objects' return error message, got {}".format(str(response)))
            raise Exception("'get_objects' return error message")

        lcc.set_step("Get '1.14.0' contract history")
        params = [self.contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract_history' with params: '{}'".format(params))

        lcc.set_step("Check '1.14.0' contract history")
        check_that(
            "''1.14.0' contract history'",
            response["result"], is_not_none(), quiet=True
        )
