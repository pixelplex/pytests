# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_true, is_, require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_by_address'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_by_address")
@lcc.suite("Check work of method 'get_account_by_address'", rank=1)
class GetAccountByAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_by_address'")
    def method_main_check(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create account address for new account")
        label = get_random_string
        broadcast_result = self.utils.perform_account_address_create_operation(self, new_account, label,
                                                                               self.__database_api_identifier)
        account_address_object = self.get_operation_results_ids(broadcast_result)

        lcc.set_step("Get objects 'impl_account_address_object_type'")
        param = [[account_address_object]]
        response_id = self.send_request(self.get_request("get_objects", param), self.__database_api_identifier)
        account_address = self.get_response(response_id)["result"][0]["address"]

        lcc.set_step("Get created account by created account_address")
        params = [account_address]
        response_id = self.send_request(self.get_request("get_account_by_address", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_by_address' of new account '{}'".format(new_account))

        lcc.set_step("Check response from method 'get_account_by_address'")
        if not self.validator.is_account_id(response["result"]):
            lcc.log_error("Wrong format of 'response', got: {}".format(response["result"]))
        else:
            lcc.log_info("'response' has correct format: account_object_type")

        check_that(
            "'account by address'",
            response["result"],
            is_(new_account)
        )


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_account_by_address")
@lcc.suite("Positive testing of method 'get_account_by_address'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Generate multiple addresses of one account")
    @lcc.depends_on("DatabaseApi.GetAccountByAddress.GetAccountByAddress.method_main_check")
    def generate_multiple_addresses(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string
        addresses_count = 2
        account_addresses = []

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create multiple account address for new account")
        for i in range(addresses_count):
            self.utils.perform_account_address_create_operation(self, new_account, label + str(i),
                                                                self.__database_api_identifier)

        lcc.set_step("Get addresses of created account in the network and store addresses")
        _from, limit = 0, 100
        params = [new_account, _from, limit]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        for i in range(len(response)):
            account_addresses.append(response[i]["address"])
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check that generating addresses are not the same")
        for i in range(len(account_addresses)):
            if i != len(account_addresses) - 1:
                require_that(
                    "'generating addresses are not the same'",
                    account_addresses[i] != account_addresses[i + 1], is_true()
                )

        lcc.set_step("Get created account by created account_addresses")
        for i in range(len(account_addresses)):
            params = [account_addresses[i]]
            response_id = self.send_request(self.get_request("get_account_by_address", params),
                                            self.__database_api_identifier)
            response = self.get_response(response_id)
            lcc.log_info("Get account by address #{}".format(i))
            check_that(
                "'account by address'",
                response["result"],
                is_(new_account)
            )
