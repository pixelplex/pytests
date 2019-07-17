# -*- coding: utf-8 -*-
import random

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, this_dict, check_that_entry, has_length, is_str, equal_to, \
    require_that, not_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_addresses'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_account_addresses")
@lcc.suite("Check work of method 'get_account_addresses'", rank=1)
class GetAccountAddresses(BaseTest):

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
    @lcc.test("Simple work of method 'get_account_addresses'")
    def method_main_check(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string
        _from = 0
        limit = 100

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get addresses of created account in the network")
        params = [new_account, _from, limit]
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
        self.utils.perform_account_address_create_operation(self, new_account, label,
                                                            self.__database_api_identifier)
        lcc.log_info("Account address create operation for new account performed")

        lcc.set_step("Get updated list of addresses of created account in the network")
        params = [new_account, _from, limit]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check new account address object in method 'get_account_addresses'")
        result = response["result"][0]
        with this_dict(result):
            if check_that("account_addresses", result, has_length(5)):
                if not self.validator.is_account_address_id(result["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
                else:
                    lcc.log_info("'id' has correct format: account_address_object_type")
                if not self.validator.is_account_id(result["owner"]):
                    lcc.log_error("Wrong format of 'owner', got: {}".format(result["owner"]))
                else:
                    lcc.log_info("'owner' has correct format: account_object_type")
                check_that_entry("label", is_str(), quiet=True)
                if not self.validator.is_hex(result["address"]):
                    lcc.log_error("Wrong format of 'address', got: {}".format(result["owner"]))
                else:
                    lcc.log_info("'address' has correct format: hex")
                check_that_entry("extensions", is_list(), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_account_addresses")
@lcc.suite("Positive testing of method 'get_account_addresses'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def proliferate_label_names(label_name_base, total_label_count):
        return ['{}{}'.format(label_name_base, 'A' * num) for num in range(total_label_count)]

    @staticmethod
    def get_random_amount(_to, _from=0):
        return round(random.uniform(_from, _to))

    def get_account_addresses(self, account_id, _from=0, limit=100):
        params = [account_id, _from, limit]
        response_id = self.send_request(self.get_request("get_account_addresses", params),
                                        self.__database_api_identifier)
        return self.get_response(response_id)

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
    @lcc.test("Create multiple addresses for new account")
    @lcc.depends_on("DatabaseApi.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def create_multiple_addresses(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        total_addresses_count = 2

        lcc.set_step("Generate address labels")
        label_name_base = get_random_string
        generated_labels = self.proliferate_label_names(label_name_base, total_addresses_count)
        lcc.log_info('Generated address labels: {}'.format(generated_labels))

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create two account address for new account")
        for i in range(total_addresses_count):
            self.utils.perform_account_address_create_operation(self, new_account, generated_labels[i],
                                                                self.__database_api_identifier)
            lcc.log_info("Account address create operation #'{}' for new account performed".format(str(i)))

        lcc.set_step("Get list of addresses of created account in the network")
        response = self.get_account_addresses(new_account)
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Check that two account addresses objects created")
        result = response["result"]
        require_that("'account address count'", result, has_length(total_addresses_count))

        address_obj1 = result[0]
        address_obj2 = result[1]
        require_that("'account address1 label1'", address_obj1["label"], equal_to(generated_labels[0]))
        require_that("'account address2 label2'", address_obj2["label"], equal_to(generated_labels[1]))

        with this_dict(address_obj1):
            check_that_entry("id", not_equal_to(address_obj2["id"]), quiet=True)
            check_that_entry("owner", equal_to(address_obj2["owner"]), quiet=True)
            check_that_entry("label", not_equal_to(address_obj2["label"]), quiet=True)
            check_that_entry("address", not_equal_to(address_obj2["address"]), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check work of from and limit param")
    @lcc.depends_on("DatabaseApi.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def check_from_and_limit_param(self, get_random_valid_account_name, get_random_string,
                                   get_random_integer_up_to_hundred):
        new_account = get_random_valid_account_name
        total_addresses_count = get_random_integer_up_to_hundred
        label = get_random_string

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create random account address for new account. Random number: '{}'".format(total_addresses_count))
        self.utils.perform_account_address_create_operation(self, new_account, label, self.__database_api_identifier,
                                                            operation_count=total_addresses_count)
        lcc.log_info("Account address create operation for new account performed. '{}' addresses created".format(
            str(total_addresses_count)))

        lcc.set_step("Get list of addresses of created account in the network")
        _from, limit = 0, 100
        response = self.get_account_addresses(new_account)
        lcc.log_info(
            "Call method 'get_account_addresses' of new account, with from='{}', limit='{}' parameters".format(_from,
                                                                                                               limit))

        lcc.set_step("Check that needed count of addresses created")
        require_that("'account addresses count'", response["result"], has_length(total_addresses_count))

        lcc.set_step("Get list of addresses of created account in the network")
        _from = self.get_random_amount(total_addresses_count)
        response = self.get_account_addresses(new_account, _from=_from)
        lcc.log_info(
            "Call method 'get_account_addresses' of new account, with from='{}', limit='{}' parameters".format(_from,
                                                                                                               limit))

        lcc.set_step("Check 'from' parameter")
        check_that("'account addresses count'", response["result"], has_length(total_addresses_count - _from))

        lcc.set_step("Get list of addresses of created account in the network")
        temp = self.get_random_amount(total_addresses_count)
        _from, limit = 0, total_addresses_count - temp
        response = self.get_account_addresses(new_account, limit=limit)
        lcc.log_info(
            "Call method 'get_account_addresses' of new account, with from='{}', limit='{}' parameters".format(_from,
                                                                                                               limit))

        lcc.set_step("Check 'limit' parameter, it less than the number of addresses")
        check_that("'account addresses count'", response["result"], has_length(total_addresses_count - temp))

        lcc.set_step("Get list of addresses of created account in the network")
        limit = total_addresses_count + 1
        response = self.get_account_addresses(new_account, limit=limit)
        lcc.log_info(
            "Call method 'get_account_addresses' of new account, with from='{}', limit='{}' parameters".format(_from,
                                                                                                               limit))

        lcc.set_step("Check 'limit' parameter, it more than the number of addresses")
        check_that("'account addresses count'", response["result"], has_length(total_addresses_count))

    @lcc.prop("type", "method")
    @lcc.test("Compare response from 'get_account_addresses' and 'get_objects' impl_account_address_object_type")
    @lcc.depends_on("DatabaseApi.GetAccountAddresses.GetAccountAddresses.method_main_check")
    def compare_with_method_get_objects(self, get_random_valid_account_name, get_random_string):
        new_account = get_random_valid_account_name
        label = get_random_string

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Create account address for new account. Store account address object")
        broadcast_result = self.utils.perform_account_address_create_operation(self, new_account, label,
                                                                               self.__database_api_identifier)
        account_address_object = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Account address create operation for new account performed. Account address object stored")

        lcc.set_step("Get addresses of created account in the network")
        response = self.get_account_addresses(new_account)["result"][0]
        lcc.log_info("Call method 'get_account_addresses' of new account")

        lcc.set_step("Get objects 'impl_account_address_object_type'")
        param = [[account_address_object]]
        response_id = self.send_request(self.get_request("get_objects", param), self.__database_api_identifier)
        response_from_get_objects = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_objects' with account address object of new account")

        lcc.set_step("Compare address object from 'get_account_addresses' and 'get_objects'")
        with this_dict(response):
            if check_that("account_addresses", response, has_length(5)):
                check_that_entry("id", equal_to(response_from_get_objects["id"]))
                check_that_entry("owner", equal_to(response_from_get_objects["owner"]))
                check_that_entry("label", equal_to(response_from_get_objects["label"]))
                check_that_entry("address", equal_to(response_from_get_objects["address"]))
                check_that_entry("extensions", equal_to(response_from_get_objects["extensions"]))
