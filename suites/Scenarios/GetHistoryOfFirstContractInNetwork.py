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
        self.contract_id = "{}0".format(self.get_object_type(self.echo.config.object_types.CONTRACT))

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
    def get_history_of_first_contract_scenario(self):
        stop, start = "1.6.0", "1.6.0"
        limit = 100

        lcc.set_step("Check that '{}' first contract in the network or not".format(self.contract_id))
        response_id = self.send_request(self.get_request("get_objects", [[self.contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"] == [None]:
            lcc.set_step("Perform create contract operation".format(self.contract_id))
            self.contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                          self.__database_api_identifier)
        elif "error" in response:
            lcc.log_error("'get_objects' return error message, got {}".format(str(response)))
            raise Exception("'get_objects' return error message")

        lcc.set_step("Get '{}' first contract history".format(self.contract_id))
        params = [self.contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract_history' with params: '{}'".format(params))

        lcc.set_step("Check '{}' first contract history".format(self.contract_id))
        check_that(
            "''{}' contract history'".format(self.contract_id),
            response["result"], is_not_none(), quiet=True
        )
