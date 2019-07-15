# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, equal_to, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_key_references'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_key_references")
@lcc.suite("Check work of method 'get_key_references'", rank=1)
class GetKeyReferences(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.nathan_name = "nathan"

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_key_references'")
    def method_main_check(self):
        lcc.set_step("Get the account by name and store his echorand_key")
        account_info = self.get_account_by_name(self.nathan_name, self.__database_api_identifier)
        echorand_key = account_info["result"]["echorand_key"]
        lcc.log_info(
            "Get default account '{}' by name and store his echorand_key: '{}'".format(self.nathan_name, echorand_key))

        lcc.set_step("Get account ID associated with the given key")
        response_id = self.send_request(self.get_request("get_key_references", [[echorand_key]]),
                                        self.__database_api_identifier)
        referenced_id = self.get_response(response_id)["result"][0][0]
        lcc.log_info("Get account id: '{}' associated with key: '{}'".format(referenced_id, echorand_key))

        lcc.set_step("Get account by referenced id")
        response_id = self.send_request(self.get_request("get_accounts", [[referenced_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_accounts' with param: '{}'".format(referenced_id))

        lcc.set_step("Check simple work of method 'get_key_references'")
        check_that("'account name'", result["name"], equal_to(self.nathan_name), quiet=True)
        check_that("'echorand_key'", result["echorand_key"], equal_to(echorand_key), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_key_references")
@lcc.suite("Positive testing of method 'get_key_references'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method 'get_key_references' with multiple keys")
    @lcc.depends_on("DatabaseApi.GetKeyReferences.GetKeyReferences.method_main_check")
    def call_method_with_multiple_keys(self):
        initial_accounts_names = ["init0", "init1"]
        echorand_keys = []
        referenced_ids = []

        lcc.set_step("Get initial accounts by name and store their echorand keys")
        for i in range(len(initial_accounts_names)):
            account_info = self.get_account_by_name(initial_accounts_names[i], self.__database_api_identifier)
            echorand_keys.append(account_info["result"]["echorand_key"])
            lcc.log_info(
                "Get default account '{}' by name and store his echorand_key: '{}'".format(initial_accounts_names[i],
                                                                                           echorand_keys[i]))

        lcc.set_step("Get accounts IDs associated with the given keys")
        response_id = self.send_request(self.get_request("get_key_references", [echorand_keys]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        for i in range(len(response)):
            referenced_ids.append(response[i][0])
            lcc.log_info("Get account id: '{}' associated with key: '{}'".format(referenced_ids[i], echorand_keys[i]))

        lcc.set_step("Get accounts by referenced ids")
        response_id = self.send_request(self.get_request("get_accounts", [referenced_ids]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_accounts' with param: '{}'".format(referenced_ids))

        lcc.set_step("Check work of method 'get_key_references' with multiple keys")
        for i in range(len(result)):
            check_that("'account name'", result[i]["name"], equal_to(initial_accounts_names[i]), quiet=True)
            check_that("'echorand_key'", result[i]["echorand_key"], equal_to(echorand_keys[i]), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Use 'get_key_references' with crated account")
    @lcc.depends_on("DatabaseApi.GetKeyReferences.GetKeyReferences.method_main_check")
    def use_method_with_created_account(self, get_random_valid_account_name, get_random_integer):
        new_account_name = get_random_valid_account_name
        callback = get_random_integer

        lcc.set_step("Register an account in the ECHO network and store his data")
        generate_keys = self.generate_keys()
        echorand_key = generate_keys[1]
        account_params = [callback, new_account_name, echorand_key, echorand_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        self.get_response(response_id)
        self.get_notice(callback, log_response=False)
        lcc.log_info("Account '{}' created. Public key: '{}'".format(new_account_name, echorand_key))

        lcc.set_step("Get accounts IDs associated with the given public key")
        response_id = self.send_request(self.get_request("get_key_references", [[echorand_key]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0][0]
        lcc.log_info("Get response from 'get_key_references' using private and public key")

        lcc.set_step("Check method work with the given public key")
        if not self.validator.is_account_id(response):
            lcc.log_error("Wrong format of 'id', got: {}".format(response))
        else:
            lcc.log_info("'id' has correct format using 'public key': account_id")

        lcc.set_step("Get account by referenced id")
        response_id = self.send_request(self.get_request("get_accounts", [[response]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        lcc.log_info("Call method 'get_accounts' with param: '{}'".format(response))

        lcc.set_step("Check work of method 'get_key_references' with created account")
        check_that("'account name'", result["name"], equal_to(new_account_name), quiet=True)
        check_that("'echorand_key'", result["echorand_key"], equal_to(echorand_key), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check method 'get_key_references' with no one's echorand_key")
    @lcc.depends_on("DatabaseApi.GetKeyReferences.GetKeyReferences.method_main_check")
    def check_method_with_no_ones_echorand_key(self):
        generate_keys = self.generate_keys()
        echorand_key = generate_keys[1]

        response_id = self.send_request(self.get_request("get_key_references", [[echorand_key]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)["result"]
        check_that("response", response, is_list([[]]), quiet=True)


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("asset_api", "get_key_references")
@lcc.suite("Negative testing of method 'get_key_references'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method with private key")
    @lcc.depends_on("DatabaseApi.GetKeyReferences.GetKeyReferences.method_main_check")
    def call_method_with_private_key(self, get_random_valid_account_name, get_random_integer):
        new_account_name = get_random_valid_account_name
        callback = get_random_integer

        lcc.set_step("Register an account in the ECHO network and store his data")
        generate_keys = self.generate_keys()
        private_key = generate_keys[0]
        echorand_key = generate_keys[1]
        account_params = [callback, new_account_name, echorand_key, echorand_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        self.get_response(response_id)
        self.get_notice(callback, log_response=False)
        lcc.log_info("Account '{}' created. Private key: '{}', public key: '{}'".format(new_account_name, private_key,
                                                                                        echorand_key))

        lcc.set_step("Call method with the given private key")
        response_id = self.send_request(self.get_request("get_key_references", [[private_key]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_key_references' return error message",
            response, has_entry("error"), quiet=True,
        )
