# -*- coding: utf-8 -*-
import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_list, this_dict, is_not_none

from project import init0, EXECUTION_STATUS_PATH
from common.base_test import BaseTest
SUITE = {
    "description": "Method 'get_balance_objects'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_balance_objects")
@lcc.suite("Check work of method 'get_balance_objects'", rank=1)
class GetBalanceObjects(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.public_key = None
        self.init0 = "init0"

    def check_status_file(self):
        self.state = True
        if not os.path.exists(EXECUTION_STATUS_PATH):
            with open(EXECUTION_STATUS_PATH, "w") as file:
                file.write(json.dumps({"get_balance_objects": True}))
        else:
            execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
            if execution_status["get_balance_objects"]:
                execution_status["get_balance_objects"] = False
                self.state = False
                file = open(EXECUTION_STATUS_PATH, "w")
                file.write(json.dumps(execution_status))
                file.close()
            else:
                self.state = False

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Check execution status")
        self.check_status_file()
        if self.state:
            lcc.set_step("Setup for {}".format(self.__class__.__name__))
            self.__database_api_identifier = self.get_identifier("database")
            lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
            lcc.set_step("Get account public key.")
            self.public_key = self.get_account_by_name(self.init0,
                                                       self.__database_api_identifier)["result"]["echorand_key"]
            lcc.log_info("{}".format(self.public_key))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_balance_objects'")
    def method_main_check(self):
        if self.state:
            lcc.set_step("Get balance objects by public key")
            response_id = self.send_request(self.get_request("get_balance_objects", [[self.public_key]]),
                                            self.__database_api_identifier, debug_mode=False)
            result = self.get_response(response_id, log_response=False, debug_mode=False)["result"][0]
            lcc.log_info("'balance objects' result is {}".format(result))
            with this_dict(result):
                if not self.validator.is_balance_id(result["id"]):
                    lcc.log_error("Wrong format of 'balance_id', got: {}".format(result["id"]))
                else:
                    lcc.log_info("'balance_id' has correct format: balance_id")
                if not self.validator.is_iso8601(result["last_claim_date"]):
                    lcc.log_error("Wrong format of 'last_claim_date', got: {}".format(result["last_claim_date"]))
                else:
                    lcc.log_info("'last_claim_date' has correct format: last_claim_date")
                with this_dict(result["balance"]):
                    self.check_uint256_numbers(result["balance"], "amount", quiet=True)
                    if not self.validator.is_asset_id(result["balance"]["asset_id"]):
                        lcc.log_error("Wrong format of 'asset_id', got: {}".format(result["balance"]["asset_id"]))
                    else:
                        lcc.log_info("'asset_id' has correct format: asset_id")
        else:
            lcc.log_info("Method GetBalanceObjects already done.")


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_balance_objects")
@lcc.suite("Positive testing of method 'get_balance_objects'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.init0_account_name = "init0"
        self.init1_account_name = "init1"

    def read_execution_status(self):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        self.state = execution_status["get_balance_objects"]


    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Check execution status")
        self.read_execution_status()
        if self.state:
            self._connect_to_echopy_lib()
            lcc.set_step("Setup for {}".format(self.__class__.__name__))
            self.__database_api_identifier = self.get_identifier("database")
            lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Get balance objects for several accounts")
    @lcc.depends_on("DatabaseApi.GetBalanceObjects.GetBalanceObjects.method_main_check")
    def get_balance_objects_for_several_address(self):
        if self.state:
            lcc.set_step("Get account by name for accounts")
            init0_account_info = self.get_account_by_name(self.init0_account_name, self.__database_api_identifier)
            init1_account_info = self.get_account_by_name(self.init1_account_name, self.__database_api_identifier)
            public_key0 = init0_account_info["result"]["echorand_key"]
            public_key1 = init1_account_info["result"]["echorand_key"]
            lcc.log_info("Get public keys for accounts")

            lcc.set_step("Get balance objects by several public key")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key0, public_key1]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"]
            lcc.log_info("{}".format(result))
            for balance in result:
                lcc.check_that("balance", balance, is_not_none())
        else:
            lcc.log_info("Test 'get_balance_objects_for_several_address' already done.")

    @lcc.prop("type", "method")
    @lcc.test("Get balance object and claim balance")
    @lcc.depends_on("DatabaseApi.GetBalanceObjects.GetBalanceObjects.method_main_check")
    def check_claim_balance_method(self):
        if self.state:
            lcc.set_step("Get account by name for init0")
            account_info = self.get_account_by_name(self.init0_account_name, self.__database_api_identifier)
            account_id = account_info["result"]["id"]
            public_key = account_info["result"]["echorand_key"]
            lcc.log_info("Get 'account_id': {} and 'public_key': {}".format(account_id, public_key))
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"][0]
            lcc.log_info("Init0 balance amount:{}".format(result["balance"]["amount"]))
            needed_amount = int(result["balance"]["amount"])
            balance_id = result["id"]
            lcc.set_step("Claim init0 balance")
            operation = self.echo_ops.get_balance_claim_operation(echo=self.echo, deposit_to_account=account_id,
                                                                  balance_owner_public_key=public_key,
                                                                  value_amount=needed_amount,
                                                                  balance_owner_private_key=init0,
                                                                  balance_to_claim=balance_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier,
                                                          debug_mode=False)

            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                    log_broadcast=False, debug_mode=False)
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            lcc.set_step("Get balance object after claim")
            result = self.get_response(response_id)["result"]
            lcc.log_info("Balance object is {}".format(result))
        else:
            lcc.log_info("Test 'check_claim_balance_method' already done.")
