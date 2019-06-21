# -*- coding: utf-8 -*-


import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, is_not_none

from common.base_test import BaseTest
SUITE = {
    "description": "Method 'get_vested_balances'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_vested_balances")
@lcc.suite("Check work of method 'get_vested_balances'", rank=1)
class GetVestedBalance(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.init2 = "init2"

    def setup_suite(self):
        if self.utils.check_accounts_have_initial_balances([self.init2]):
            super().setup_suite()
            lcc.set_step("Check execution status")
            lcc.set_step("Setup for {}".format(self.__class__.__name__))
            self.__database_api_identifier = self.get_identifier("database")
            lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
            lcc.set_step("Get account public key.")
            self.public_key = self.get_account_by_name(self.init2,
                                                       self.__database_api_identifier)["result"]["echorand_key"]
            lcc.log_info("{}".format(self.public_key))
        else:
            lcc.log_error("account: {}, is not in genesis".format(self.init2))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_vested_balances'")
    def method_main_check(self):
        lcc.set_step("Get balance objects by public key")
        response_id = self.send_request(self.get_request("get_balance_objects", [[self.public_key]]),
                                        self.__database_api_identifier, debug_mode=False)
        balance_id = self.get_response(response_id, log_response=False, debug_mode=False)["result"][0]["id"]
        lcc.set_step("Get vested balance for init2 account")
        response_id = self.send_request(self.get_request("get_vested_balances", [[balance_id]]),
                                        self.__database_api_identifier, debug_mode=False)
        result = self.get_response(response_id, log_response=False, debug_mode=False)["result"][0]
        lcc.set_step("Check result of 'vested balance' method")
        with this_dict(result):
            self.check_uint256_numbers(result, "amount", quiet=True)
            if not self.validator.is_asset_id(result["asset_id"]):
                lcc.log_error("Wrong format of 'asset_id', got: {}".format(result["asset_id"]))
            else:
                lcc.log_info("'asset_id' has correct format: asset_id")


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_vested_balances")
@lcc.suite("Positive testing of method 'get_vested_balances'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.accounts = ["init2", "init3"]

    def setup_suite(self):
        if self.utils.check_accounts_have_initial_balances(self.accounts):
            super().setup_suite()
            self._connect_to_echopy_lib()
            lcc.set_step("Setup for {}".format(self.__class__.__name__))
            self.__database_api_identifier = self.get_identifier("database")
            lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        else:
            lcc.log_error("accounts: {}, is not in genesis".format(self.accounts))


    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Get vested balances for several accounts")
    @lcc.depends_on("DatabaseApi.GetVestedBalance.GetVestedBalance.method_main_check")
    def get_vested_balance_for_several_address(self):
        lcc.set_step("Get public_keys for accounts")
        public_keys = []
        for i, account in enumerate(self.accounts):
            public_keys.append(self.get_account_by_name(account, self.__database_api_identifier)
                               ["result"]["echorand_key"])
        lcc.log_info("accounts public_keys {}".format(public_keys))
        lcc.set_step("Get balance objects by several public key")
        response_id = self.send_request(self.get_request("get_balance_objects", [public_keys]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        account_balance_id = []
        lcc.set_step("Get balance id of accounts")
        for balance_object in result:
            account_balance_id.append(balance_object["id"])
        lcc.log_info("balance id: {}".format(account_balance_id))
        lcc.set_step("Get vested balance for several accounts")

        response_id = self.send_request(self.get_request("get_vested_balances",
                                        [account_balance_id]),
                                        self.__database_api_identifier, debug_mode=True)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Get 'get_vested_balances' method response: {}".format(result))
        for vested_assets in result:
                lcc.check_that("vested_assets", vested_assets, is_not_none())
