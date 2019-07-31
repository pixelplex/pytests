# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, is_not_none, has_length, check_that

from common.base_test import BaseTest
from project import ROPSTEN

SUITE = {
    "description": "Method 'get_vested_balances'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_vested_balances")
@lcc.suite("Check work of method 'get_vested_balances'", rank=1)
class GetVestedBalances(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.public_key = None
        self.init2_account_name = "init2"

    def setup_suite(self):
        if not ROPSTEN:
            super().setup_suite()
            if self.utils.check_accounts_have_initial_balances([self.init2_account_name]):
                lcc.set_step("Check execution status")
                lcc.set_step("Setup for {}".format(self.__class__.__name__))
                self.__database_api_identifier = self.get_identifier("database")
                lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
                self.public_key = self.get_account_by_name(self.init2_account_name,
                                                           self.__database_api_identifier)["result"]["echorand_key"]
                lcc.log_info("'{}' account public key: '{}'".format(self.init2_account_name, self.public_key))
            else:
                lcc.log_error("'{}' account does not have initial balance in genesis".format(self.init2_account_name))
        else:
            lcc.log_warn("Tests did not run in the local network. Test of method 'get_vested_balances' was skipped.")

    def teardown_suite(self):
        if not ROPSTEN:
            super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_vested_balances'")
    def method_main_check(self):
        if not ROPSTEN:
            lcc.set_step("Get balance objects by public key")
            response_id = self.send_request(self.get_request("get_balance_objects", [[self.public_key]]),
                                            self.__database_api_identifier)
            balance_id = self.get_response(response_id)["result"][0]["id"]
            lcc.log_info("Call method 'get_balance_objects' with param: '{}'".format(self.public_key))

            lcc.set_step("Get vested balance of '{}' account".format(self.init2_account_name))
            response_id = self.send_request(self.get_request("get_vested_balances", [[balance_id]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"][0]
            lcc.log_info("Call method 'get_vested_balances' with param: '{}'".format(balance_id))

            lcc.set_step("Check simple work of method 'vested balance'")
            with this_dict(result):
                if check_that("balance_object", result, has_length(2)):
                    self.check_uint256_numbers(result, "amount", quiet=True)
                    if not self.validator.is_asset_id(result["asset_id"]):
                        lcc.log_error("Wrong format of 'asset_id', got: {}".format(result["asset_id"]))
                    else:
                        lcc.log_info("'asset_id' has correct format: asset_id")
        else:
            lcc.log_warn("Tests did not run in the local network. Test of method 'get_vested_balances' was skipped.")


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_vested_balances")
@lcc.suite("Positive testing of method 'get_vested_balances'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.init2_account_name = "init2"
        self.init3_account_name = "init3"

    def setup_suite(self):
        if not ROPSTEN:
            super().setup_suite()
            if self.utils.check_accounts_have_initial_balances([self.init2_account_name, self.init3_account_name]):
                super().setup_suite()
                self._connect_to_echopy_lib()
                lcc.set_step("Setup for {}".format(self.__class__.__name__))
                self.__database_api_identifier = self.get_identifier("database")
                lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
            else:
                lcc.log_error("'{}', '{}' accounts do not have initial balances in genesis"
                              "".format(self.init2_account_name, self.init3_account_name))
        else:
            lcc.log_warn("Tests did not run in the local network. Test of method 'get_vested_balances' was skipped.")

    def teardown_suite(self):
        if not ROPSTEN:
            self._disconnect_to_echopy_lib()
            super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Get vested balances for several accounts")
    @lcc.depends_on("DatabaseApi.GetVestedBalances.GetVestedBalances.method_main_check")
    def get_vested_balance_for_several_address(self):
        if not ROPSTEN:
            lcc.set_step("Get accounts public keys and store")
            public_key_init2 = self.get_account_by_name(
                self.init2_account_name, self.__database_api_identifier)["result"]["echorand_key"]
            public_key_init3 = self.get_account_by_name(
                self.init3_account_name, self.__database_api_identifier)["result"]["echorand_key"]
            lcc.log_info("'{}' public key: '{}'".format(self.init2_account_name, public_key_init2))
            lcc.log_info("'{}' public key: '{}'".format(self.init3_account_name, public_key_init3))

            lcc.set_step("Get balance objects by several public key and store")
            params = [public_key_init2, public_key_init3]
            response_id = self.send_request(self.get_request("get_balance_objects", [params]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"]
            lcc.log_info("Call method 'get_balance_objects' with params: '{}'".format(params))

            account_balance_ids = []
            for balance_object in result:
                account_balance_ids.append(balance_object["id"])
            lcc.log_info("Stored accounts balance ids: '{}'".format(account_balance_ids))

            lcc.set_step("Get vested balance for several accounts")
            response_id = self.send_request(self.get_request("get_vested_balances", [account_balance_ids]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"]
            lcc.log_info("Call method 'get_vested_balances' with params: '{}'".format(account_balance_ids))

            lcc.set_step("Check response from 'get_vested_balances' method")
            for vested_assets in result:
                check_that("vested_assets", vested_assets, is_not_none())
        else:
            lcc.log_warn("Tests did not run in the local network. Test of method 'get_vested_balances' was skipped.")
