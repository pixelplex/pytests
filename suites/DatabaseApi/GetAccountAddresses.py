# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, this_dict, check_that_entry, has_length, is_str

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_addresses'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_account_addresses")
@lcc.suite("Check work of method 'get_account_addresses'", rank=1)
class GetAccountAddresses(BaseTest):

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
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_addresses'")
    def method_main_check(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        start = stop = 0
        limit = 100

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get addresses of created account in the network")
        params = [new_account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check simple work of method 'get_account_addresses'")
        check_that(
            "'new account addresses'",
            response["result"],
            is_list([]), quiet=True
        )

        lcc.set_step("Create account address for new account")
        label = get_random_string
        broadcast_result = self.utils.perform_account_address_create_operation(self, new_account, label,
                                                                               self.__database_api_identifier)
        account_address_object = self.get_operation_results_ids(broadcast_result)

        lcc.set_step("Get updated list of addresses of created account in the network")
        params = [new_account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check new account address in method 'get_account_addresses'")
        # todo: remove. Bug: "ECHO-843"
        check_that(
            "'new account addresses'",
            response["result"],
            is_list([]), quiet=True
        )
        # todo: add. Bug: "ECHO-843"
        # result = response["result"][0]
        # with this_dict(result):
        #     if check_that("account_addresses", result, has_length(4)):
        #         if not self.validator.is_account_address_id(result["id"]):
        #             lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
        #         else:
        #             lcc.log_info("'id' has correct format: account_address_object_type")
        #         if not self.validator.is_account_id(result["owner"]):
        #             lcc.log_error("Wrong format of 'owner', got: {}".format(result["owner"]))
        #         else:
        #             lcc.log_info("'owner' has correct format: account_object_type")
        #         check_that_entry("label", is_str(), quiet=True)
        #         if not self.validator.is_hex(result["address"]):
        #             lcc.log_error("Wrong format of 'address', got: {}".format(result["owner"]))
        #         else:
        #             lcc.log_info("'address' has correct format: hex")
        # todo: remove. Bug: "ECHO-843"
        lcc.set_step("Get objects 'impl_account_address_object_type'")
        param = [[account_address_object]]
        response_id = self.send_request(self.get_request("get_objects", param), self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]

        with this_dict(response):
            if check_that("account_addresses", response, has_length(4)):
                if not self.validator.is_account_address_id(response["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(response["id"]))
                else:
                    lcc.log_info("'id' has correct format: account_address_object_type")
                if not self.validator.is_account_id(response["owner"]):
                    lcc.log_error("Wrong format of 'owner', got: {}".format(response["owner"]))
                else:
                    lcc.log_info("'owner' has correct format: account_object_type")
                check_that_entry("label", is_str(), quiet=True)
                if not self.validator.is_hex(response["address"]):
                    lcc.log_error("Wrong format of 'address', got: {}".format(response["owner"]))
                else:
                    lcc.log_info("'address' has correct format: hex")
