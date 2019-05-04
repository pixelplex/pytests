# -*- coding: utf-8 -*-
import random
import string

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, has_entry, is_none, is_not_none

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "Registration Api"
}


@lcc.prop("testing", "main")
@lcc.tags("registration_api")
@lcc.suite("Registration API", rank=1)
class RegistrationApi(object):

    @lcc.tags("connection_to_registration_api")
    @lcc.test("Check connection to RegistrationApi")
    def connection_to_registration_api(self, get_random_valid_account_name, get_random_integer):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a Registration API")
        api_identifier = base.get_identifier("registration")
        check_that("'registration api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Registration api identifier. Call registration api method 'register_account'")
        generate_keys = base.generate_keys()
        public_key = generate_keys[1]
        memo_key = generate_keys[2]
        callback = get_random_integer
        account_params = [callback, get_random_valid_account_name, public_key, public_key, memo_key, public_key]
        response_id = base.send_request(base.get_request("register_account", account_params), api_identifier)
        response = base.get_response(response_id)
        base.get_notice(callback)

        check_that(
            "'call method 'register_account''",
            response["result"], is_none(), quiet=False
        )

        lcc.set_step("Check that Registration api identifier is unique")
        generate_keys = base.generate_keys()
        public_key = generate_keys[1]
        memo_key = generate_keys[2]
        account_params = [callback, get_random_valid_account_name, public_key, public_key, memo_key, public_key]
        response_id = base.send_request(base.get_request("register_account", account_params), api_identifier + 1)
        response = base.get_response(response_id, negative=True)

        check_that(
            "'using another identifier gives an error'",
            response, has_entry("error"), quiet=True
        )

        base.ws.close()


@lcc.prop("testing", "positive")
@lcc.tags("registration_api")
@lcc.suite("Positive testing of method 'register_account'", rank=2)
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
    @lcc.test("Registration with valid credential")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def registration_with_valid_credential(self, get_random_valid_account_name, get_random_integer):
        lcc.set_step("Registration an account")
        new_account = get_random_valid_account_name
        callback = get_random_integer
        generate_keys = self.generate_keys()
        public_key = generate_keys[1]
        memo_key = generate_keys[2]
        account_params = [callback, new_account, public_key, public_key, memo_key, public_key]
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


@lcc.prop("testing", "negative")
@lcc.tags("registration_api")
@lcc.suite("Negative testing of method 'register_account'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "Registration API identifiers is '{}'".format(self.__registration_api_identifier))

    def get_random_character(self, random_def, not_hyphen=False):
        character = random_def
        if not_hyphen and character == "-":
            return self.get_random_character(random_def, not_hyphen=True)
        return character

    @staticmethod
    def get_account_name(_from=1, _to=64):
        random_num = random.randrange(_from, _to)
        random_string = ''.join(
            random.SystemRandom().choice(string.ascii_lowercase) for _ in range(random_num))
        return random_string

    def _register_account(self, callback, new_account, public_key=None, memo_key=None):
        generate_keys = self.generate_keys()
        if public_key is None:
            public_key = generate_keys[1]
        if memo_key is None:
            memo_key = generate_keys[2]
        account_params = [callback, new_account, public_key, public_key, memo_key, public_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        self.__registration_api_identifier)
        return self.get_response(response_id, negative=True)

    @lcc.prop("type", "method")
    @lcc.test("Empty account name")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def empty_account_name(self, get_random_integer):
        lcc.set_step("Registration empty account")
        callback = get_random_integer
        new_account = ""
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Account name length longer than 63")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_length_longer_than_63(self, get_random_integer):
        lcc.set_step("Register an account with a name longer than 63")
        callback = get_random_integer
        new_account = self.get_account_name(64, 100)
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Account name start with digit")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_start_with_digit(self, get_random_integer):
        lcc.set_step("Register an account with a name that start with digit")
        callback = get_random_integer
        new_account = "1" + self.get_account_name(_to=63)
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Account name is digits")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_is_digits(self, get_random_integer):
        lcc.set_step("Register an account with a name from digits")
        callback = get_random_integer
        new_account = 123456
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Account name with a special character, not hyphen")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_with_special_character(self, get_random_integer, get_random_character):
        lcc.set_step("Register an account with a name that have a special character, not hyphen")
        callback = get_random_integer
        part1 = self.get_account_name(_to=4)
        part2 = self.get_account_name(_to=4)
        new_account = part1 + self.get_random_character(get_random_character, not_hyphen=True) + part2
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Account name end with a special character")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_end_with_special_character(self, get_random_integer, get_random_character):
        lcc.set_step("Register an account with a name that end with a special character")
        callback = get_random_integer
        new_account = self.get_account_name() + self.get_random_character(get_random_character)
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Account name is uppercase")
    @lcc.depends_on("RegistrationApi.RegistrationApi.connection_to_registration_api")
    def account_name_is_uppercase(self, get_random_integer):
        lcc.set_step("Register an account with a name that all letters are uppercase")
        callback = get_random_integer
        new_account = self.get_account_name().upper()
        response = self._register_account(callback, new_account)

        check_that(
            "'register_account' return error message",
            response, has_entry("error"), quiet=True
        )

    # todo: add check for: callback, owner ECDSA key, active ECDSA key, memo ECDSA key, ed25519 key for echorand
