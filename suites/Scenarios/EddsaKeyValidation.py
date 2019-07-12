# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Check eddsa key validation in the ECHO network"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("eddsa_key_validation")
@lcc.suite("Check scenario 'Eddsa key validation'")
class EddsaKeyValidation(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def _register_account(self, callback, account_name, active_key, echorand_key, negative=True):
        account_params = [callback, account_name, active_key, echorand_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario checks if the ECHO validates the keys in length.")
    def eddsa_key_validation_scenario(self, get_random_valid_account_name, get_random_integer_up_to_ten,
                                      get_random_character, get_random_integer):
        account_name = get_random_valid_account_name
        callback = get_random_integer

        lcc.set_step("Generate keys for account registration. Prepare input data for tests")
        generate_keys = self.generate_keys()
        public_key = generate_keys[1]
        lcc.log_info("Public key: '{}'".format(public_key))

        public_key_less_symbols = public_key[:-get_random_integer_up_to_ten]
        lcc.log_info("Public key with symbols length less than 32 bytes: '{}'".format(public_key_less_symbols))

        public_key_more_symbols = public_key + str(get_random_integer_up_to_ten)
        lcc.log_info("Public key with symbols length more than 32 bytes: '{}'".format(public_key_more_symbols))

        public_key_with_character = \
            public_key[:get_random_integer_up_to_ten] + get_random_character + \
            public_key[get_random_integer_up_to_ten + 1:]
        lcc.log_info("Public key with special character: '{}'".format(public_key_with_character))

        lcc.set_step("Register new account with addsa key length less than 32 bytes")
        response = self._register_account(callback, account_name, active_key=public_key_less_symbols,
                                          echorand_key=public_key)
        check_that("registration response", response, has_entry("error"), quiet=True)

        response = self._register_account(callback, account_name, active_key=public_key,
                                          echorand_key=public_key_less_symbols)
        check_that("registration response", response, has_entry("error"), quiet=True)

        lcc.set_step("Register new account with addsa key length more than 32 bytes")
        response = self._register_account(callback, account_name, active_key=public_key_more_symbols,
                                          echorand_key=public_key)
        check_that("registration response", response, has_entry("error"), quiet=True)

        response = self._register_account(callback, account_name, active_key=public_key,
                                          echorand_key=public_key_more_symbols)
        check_that("registration response", response, has_entry("error"), quiet=True)

        lcc.set_step("Register new account with special character")
        response = self._register_account(callback, account_name, active_key=public_key_with_character,
                                          echorand_key=public_key)
        check_that("registration response", response, has_entry("error"), quiet=True)

        response = self._register_account(callback, account_name, active_key=public_key,
                                          echorand_key=public_key_with_character)
        check_that("registration response", response, has_entry("error"), quiet=True)
