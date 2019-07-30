# -*- coding: utf-8 -*-
import re

import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError
from lemoncheesecake.matching import check_that, equal_to, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Testing Echo asset precision"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("echo_asset_precision")
@lcc.suite("Check scenario 'Echo asset precision'")
class EchoAssetPrecision(BaseTest):

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

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes check asset precision")
    def echo_asset_precision_scenario(self, get_random_valid_account_name, get_random_integer):
        new_account = get_random_valid_account_name
        transfer_amount = get_random_integer

        lcc.set_step("Get Echo asset and store its precision")
        response_id = self.send_request(self.get_request("get_assets", [[self.echo_asset]]),
                                        self.__database_api_identifier)
        asset_precision = self.get_response(response_id)["result"][0]["precision"]
        check_that("'Echo asset precision'", asset_precision, equal_to(8))

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform transfer echo asset from account with empty balance and check error")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=new_account,
                                                         to_account_id=self.echo_acc0, amount=transfer_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        try:
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            lcc.log_error("Error: broadcast transaction complete. Account with empty balance can make transfer: '{}'")
        except RPCError as e:
            lcc.log_info(str(e))

            lcc.set_step("Get error and check Echo asset precision")
            asset_precision_regex = re.compile(r"\d+\.\d+")
            amounts_in_error_message = re.findall(asset_precision_regex, str(e))
            for amount in amounts_in_error_message:
                amount = amount.split(".")
                check_that("'Echo asset precision'", str(amount[1]), has_length(8))
