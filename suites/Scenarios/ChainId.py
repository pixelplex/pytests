# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Comparing the 'chain_id' field of all methods where they are"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("chain_id")
@lcc.suite("Check scenario 'Chain id'")
class ChainId(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario comparing the 'chain_id' field of all methods where they are")
    def compare_chain_id_scenario(self):
        lcc.set_step("Get chain id")
        response_id = self.send_request(self.get_request("get_chain_id"), self.__api_identifier)
        get_chain_id_response = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_chain_id'")

        lcc.set_step("Get chain properties and store chain_id")
        response_id = self.send_request(self.get_request("get_chain_properties"), self.__api_identifier)
        get_chain_properties_response = self.get_response(response_id)["result"]["chain_id"]
        lcc.log_info("Call method 'get_chain_properties' and store 'chain_id' field")

        lcc.set_step("Compare chain_id with method 'get_chain_properties'")
        check_that(
            "'chain_id' of methods compare",
            get_chain_id_response, equal_to(get_chain_properties_response)
        )
