# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_dict, is_integer, \
    has_entry, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_chain_properties'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_chain_properties")
@lcc.suite("Check work of method 'get_chain_properties'", rank=1)
class GetChainProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_chain_properties'")
    def method_main_check(self):
        lcc.set_step("Get chain properties")
        response_id = self.send_request(self.get_request("get_chain_properties"), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_chain_properties'")

        lcc.set_step("Check main fields")
        with this_dict(response["result"]):
            if check_that("chain_properties", response["result"], has_length(4)):
                if not self.validator.is_chain_property_object_id(response["result"]["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(response["result"]["id"]))
                else:
                    lcc.log_info("'id' has correct format: chain_property_object_type")
                if not self.validator.is_hex(response["result"]["chain_id"]):
                    lcc.log_error("Wrong format of 'chain_id', got: {}".format(response["result"]["chain_id"]))
                else:
                    lcc.log_info("'chain_id' has correct format: hex")
                check_that_entry("immutable_parameters", is_dict(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)

        lcc.set_step("Check 'immutable_parameters'")
        immutable_parameters = response["result"]["immutable_parameters"]
        with this_dict(immutable_parameters):
            if check_that("immutable_parameters", immutable_parameters, has_length(1)):
                check_that_entry("min_committee_member_count", is_integer(), quiet=True)


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_chain_properties")
@lcc.suite("Negative testing of method 'get_chain_properties'", rank=2)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.tags("Bug: 'ECHO-680'")
    @lcc.depends_on("DatabaseApi.GetChainProperties.GetChainProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_chain_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_chain_properties' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
