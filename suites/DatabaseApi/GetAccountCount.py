# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, has_entry, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_count'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_count")
@lcc.suite("Check work of method 'get_account_count'", rank=1)
class GetAccountCount(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_count'")
    def method_main_check(self):
        lcc.set_step("Get the current number of accounts in the network")
        response_id = self.send_request(self.get_request("get_account_count"), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_count', account_count='{}'".format(response["result"]))

        lcc.set_step("Check simple work of method 'get_account_count'")
        check_that(
            "'account count'",
            response["result"],
            is_integer(), quiet=True
        )


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_account_count")
@lcc.suite("Positive testing of method 'get_account_count'", rank=2)
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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Register new account in the network to check 'get_account_count'")
    @lcc.depends_on("DatabaseApi.GetAccountCount.GetAccountCount.method_main_check")
    def add_new_account_in_the_network(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Get the current number of accounts in the network")
        response_id = self.send_request(self.get_request("get_account_count"), self.__database_api_identifier)
        account_count_before = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_account_count', account_count='{}'".format(account_count_before))

        lcc.set_step("Register new account in the network")
        self.get_account_id(new_account, self.__database_api_identifier, self.__registration_api_identifier)

        lcc.set_step("Get the updated number of accounts in the network")
        response_id = self.send_request(self.get_request("get_account_count"), self.__database_api_identifier)
        account_count_after = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_account_count', account_count='{}'".format(account_count_after))

        lcc.set_step("Check simple work of method 'get_account_count'")
        check_that(
            "'account count'",
            account_count_after - account_count_before,
            is_(1),
        )


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_count")
@lcc.suite("Negative testing of method 'get_account_count'", rank=3)
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
    @lcc.depends_on("DatabaseApi.GetAccountCount.GetAccountCount.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_account_count", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_account_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
