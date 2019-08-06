# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, has_entry, greater_than_or_equal_to, \
    check_that_entry, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_dynamic_global_properties'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_dynamic_global_properties")
@lcc.suite("Check work of method 'get_dynamic_global_properties'", rank=1)
class GetDynamicGlobalProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_dynamic_global_properties'")
    def method_main_check(self):
        lcc.set_step("Get dynamic global properties")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_dynamic_global_properties'")

        lcc.set_step("Check main fields")
        dynamic_global_properties = ["head_block_number", "committee_budget", "accounts_registered_this_interval",
                                     "recently_missed_count", "current_aslot", "dynamic_flags",
                                     "last_irreversible_block_num"]
        dynamic_global_properties_time = ["time", "next_maintenance_time", "last_budget_time"]
        result = response["result"]
        with this_dict(result):
            if check_that("dynamic global properties", result, has_length(14)):
                if not self.validator.is_dynamic_global_object_id(result["id"]):
                    lcc.log_error("Wrong format of 'dynamic_global_object_id', got: {}".format(result))
                else:
                    lcc.log_info("'id' has correct format: dynamic_global_object_id")

                for i in range(len(dynamic_global_properties)):
                    self.check_uint64_numbers(result, dynamic_global_properties[i], quiet=True)
                    value = int(result[dynamic_global_properties[i]])
                    check_that(dynamic_global_properties[i], value, greater_than_or_equal_to(0), quiet=True)

                if not self.validator.is_hex(result["head_block_id"]):
                    lcc.log_error("Wrong format of 'head_block_id', got: {}".format(result))
                else:
                    lcc.log_info("'head_block_id' has correct format: hex")

                for i in range(len(dynamic_global_properties_time)):
                    if not self.validator.is_iso8601(result[dynamic_global_properties_time[i]]):
                        lcc.log_error(
                            "Wrong format of '{}', got: {}".format(dynamic_global_properties_time[i],
                                                                   result[dynamic_global_properties_time[i]]))
                    else:
                        lcc.log_info("'{}' has correct format: iso8601".format(dynamic_global_properties_time[i]))
                self.check_uint256_numbers(result, "recent_slots_filled", quiet=True)
                value = int(result["recent_slots_filled"])
                check_that(result["recent_slots_filled"], value, greater_than_or_equal_to(0), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_dynamic_global_properties")
@lcc.suite("Negative testing of method 'get_dynamic_global_properties'", rank=3)
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
    @lcc.depends_on("DatabaseApi.GetDynamicGlobalProperties.GetDynamicGlobalProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_dynamic_global_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_dynamic_global_properties' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
