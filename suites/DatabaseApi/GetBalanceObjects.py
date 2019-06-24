# -*- coding: utf-8 -*-
import json
import os

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, is_not_none, check_that, has_length, is_

from common.base_test import BaseTest
from project import init0, EXECUTION_STATUS_PATH

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
        self.init0_account_name = "init0"
        self.state = None

    def check_status_file(self):
        self.state = True
        if not os.path.exists(EXECUTION_STATUS_PATH):
            with open(EXECUTION_STATUS_PATH, "w") as file:
                file.write(json.dumps({"get_balance_objects": True}))
        else:
            self.state = False

    def setup_suite(self):
        if self.utils.check_accounts_have_initial_balances([self.init0_account_name]):
            super().setup_suite()
            lcc.set_step("Check execution status")
            self.check_status_file()
            if self.state:
                lcc.set_step("Setup for {}".format(self.__class__.__name__))
                self.__database_api_identifier = self.get_identifier("database")
                lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
                self.public_key = self.get_account_by_name(self.init0_account_name,
                                                           self.__database_api_identifier)["result"]["echorand_key"]
                lcc.log_info("'{}' account public key: '{}'".format(self.init0_account_name, self.public_key))
        else:
            lcc.log_error("'{}' account does not have initial balance in genesis".format(self.init0_account_name))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_balance_objects'")
    def method_main_check(self):
        if self.state:
            lcc.set_step("Get balance objects by public key")
            response_id = self.send_request(self.get_request("get_balance_objects", [[self.public_key]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"][0]
            with this_dict(result):
                if check_that("balance_object", result, has_length(4)):
                    if not self.validator.is_balance_id(result["id"]):
                        lcc.log_error("Wrong format of 'balance_id', got: {}".format(result["id"]))
                    else:
                        lcc.log_info("'balance_id' has correct format: balance_id")
                    if not self.validator.is_iso8601(result["last_claim_date"]):
                        lcc.log_error("Wrong format of 'last_claim_date', got: {}".format(result["last_claim_date"]))
                    else:
                        lcc.log_info("'last_claim_date' has correct format: iso8601")
                    with this_dict(result["balance"]):
                        self.check_uint256_numbers(result["balance"], "amount", quiet=True)
                        if not self.validator.is_asset_id(result["balance"]["asset_id"]):
                            lcc.log_error("Wrong format of 'asset_id', got: {}".format(result["balance"]["asset_id"]))
                        else:
                            lcc.log_info("'asset_id' has correct format: asset_object_type")
        else:
            lcc.log_info("Testing of the 'get_balance_objects' method was successfully completed earlier")


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_balance_objects")
@lcc.suite("Positive testing of method 'get_balance_objects'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.init0_account_name = "init0"
        self.init1_account_name = "init1"
        self.state = None

    def read_execution_status(self):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        self.state = execution_status["get_balance_objects"]

    def setup_suite(self):
        if self.utils.check_accounts_have_initial_balances([self.init0_account_name, self.init1_account_name]):
            super().setup_suite()
            lcc.set_step("Check execution status")
            self.read_execution_status()
            if self.state:
                self._connect_to_echopy_lib()
                lcc.set_step("Setup for {}".format(self.__class__.__name__))
                self.__database_api_identifier = self.get_identifier("database")
                lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        else:
            lcc.log_error("'{}', '{}' accounts do not have initial balances in genesis".format(self.init0_account_name,
                                                                                               self.init1_account_name))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Get balance objects for several accounts")
    @lcc.depends_on("DatabaseApi.GetBalanceObjects.GetBalanceObjects.method_main_check")
    def get_balance_objects_for_several_address(self):
        if self.state:
            lcc.set_step("Get accounts public keys and store")
            public_key_init0 = self.get_account_by_name(
                self.init0_account_name, self.__database_api_identifier)["result"]["echorand_key"]
            public_key_init1 = self.get_account_by_name(
                self.init1_account_name, self.__database_api_identifier)["result"]["echorand_key"]
            lcc.log_info("'{}' public key: '{}'".format(self.init0_account_name, public_key_init0))
            lcc.log_info("'{}' public key: '{}'".format(self.init1_account_name, public_key_init1))

            lcc.set_step("Get balance objects by several public key")
            params = [public_key_init0, public_key_init1]
            response_id = self.send_request(self.get_request("get_balance_objects", [params]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"]
            lcc.log_info("Call method 'get_balance_objects' with params: '{}'".format(params))

            lcc.set_step("Check initial balances of initial accounts")
            for balance in result:
                check_that("balance", balance, is_not_none(), quiet=True)
        else:
            lcc.log_info("Testing of the 'get_balance_objects' method was successfully completed earlier")


    def change_test_status(self):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        if execution_status["get_balance_objects"]:
            execution_status["get_balance_objects"] = False
            self.state = False
            file = open(EXECUTION_STATUS_PATH, "w")
            file.write(json.dumps(execution_status))
            file.close()
        else:
            self.state = False


    def add_log_info(self, log):
        execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))
        execution_status["get_balance_objects"] = False
        file = open(EXECUTION_STATUS_PATH, "w")
        execution_status.update({"log_info": log})
        file.write(json.dumps(execution_status))
        file.close()

    @lcc.prop("type", "method")
    @lcc.test("Work of method after balance claim operation")
    @lcc.depends_on("DatabaseApi.GetBalanceObjects.GetBalanceObjects.method_main_check")
    def get_balance_objects_after_balance_claim_operation(self):
        if self.state:
            lcc.set_step("Get account id and public key and store")
            account_info = self.get_account_by_name(self.init0_account_name, self.__database_api_identifier)
            account_id = account_info["result"]["id"]
            public_key = account_info["result"]["echorand_key"]
            lcc.log_info(
                "'{}' account has id='{}' and public_key='{}'".format(self.init0_account_name,
                                                                      account_id, public_key))

            lcc.set_step("Get balance objects before balance claim operation. Store balance id and amount")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"][0]
            lcc.log_info("Call method 'get_balance_objects' with param: '{}'".format(public_key))
            balance_id = result["id"]
            balance_amount = int(result["balance"]["amount"])
            lcc.log_info(
                "'{}' account has balance with id='{}' and amount='{}'".format(self.init0_account_name, balance_id,
                                                                               balance_amount))

            lcc.set_step("Perform balance claim operation")
            operation = self.echo_ops.get_balance_claim_operation(echo=self.echo, deposit_to_account=account_id,
                                                                  balance_owner_public_key=public_key,
                                                                  value_amount=balance_amount,
                                                                  balance_owner_private_key=init0,
                                                                  balance_to_claim=balance_id)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            if self.is_operation_completed(broadcast_result, expected_static_variant=0):
                self.change_test_status()

            lcc.set_step("Get balance objects after balance claim operation")
            response_id = self.send_request(self.get_request("get_balance_objects", [[public_key]]),
                                            self.__database_api_identifier)
            result = self.get_response(response_id)["result"]
            lcc.log_info("{}".format(result))
            lcc.log_info("Call method 'get_balance_objects' with param: '{}'".format(public_key))

            lcc.set_step("Check response from 'get_balance_objects' method after balance claim operation")
            if check_that("balance", result, is_([])):
                self.add_log_info("Testing of the 'get_balance_objects' method was successfully completed earlier")
            else:
                self.add_log_info("Test of method 'get_balance_objects' failed during the previous run")
        else:
            execution_status = json.load(open(EXECUTION_STATUS_PATH, "r"))

            lcc.log_info(execution_status["log_info"])
