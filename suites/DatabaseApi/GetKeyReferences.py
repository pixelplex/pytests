# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, equal_to, is_none, is_not_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_key_references'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
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


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_key_references")
@lcc.suite("Positive testing of method 'get_key_references'", rank=2)
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
    @lcc.test("Create new account and check method 'get_key_references'")
    @lcc.depends_on("DatabaseApi.GetKeyReferences.GetKeyReferences.method_main_check")
    def check_mothod_for_new_account(self, get_random_valid_account_name, get_random_integer):
        lcc.set_step("Create new account")

        lcc.set_step("Registration an account")
        new_account = get_random_valid_account_name
        callback = get_random_integer
        generate_keys = self.generate_keys()
        public_key = generate_keys[1]
        account_params = [callback, new_account, public_key, public_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        response = self.get_response(response_id)
        self.get_notice(callback)
        check_that(
            "register account '{}'".format(new_account),
            response["result"], is_none(), quiet=False
        )

        lcc.set_step("Check that the account is registered on the network. Call method 'get_account_by_name'")
        response_id = self.send_request(self.get_request("get_account_by_name", [new_account]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        check_that(
            "'call method 'get_account_by_name''",
            response["result"], is_not_none(), quiet=True
        )
        account_info = response
        account_name = account_info["result"]["name"]
        echorand_key = account_info["result"]["echorand_key"]

        lcc.set_step("Get account ID associated with the given key")
        response_id = self.send_request(self.get_request("get_key_references", [[echorand_key]]),
                                        self.__database_api_identifier)

        response = self.get_response(response_id)
        referenced_id = response["result"]
        lcc.log_info("Get account id = {} of account = {}, associated with key = {}".format(referenced_id,
                                                                                            account_name,
                                                                                            echorand_key))
        lcc.set_step("Get account id")
        account_id = self.get_account_id(new_account, self.__database_api_identifier,
                                         self.__registration_api_identifier)

        check_that("'account id'", referenced_id[0][0], equal_to(account_id))

    @lcc.prop("type", "method")
    @lcc.test("Check method 'get_key_references' with nonexistent account")
    @lcc.depends_on("DatabaseApi.GetKeyReferences.GetKeyReferences.method_main_check")
    def check_mothod_for_new_account(self):
        generate_keys = self.generate_keys()
        echorand_key = generate_keys[1]

        response_id = self.send_request(self.get_request("get_key_references", [[echorand_key]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        account_id = response["result"]
        check_that("account_id", account_id, is_list())
        check_that("account_id", account_id, equal_to([[]]))
