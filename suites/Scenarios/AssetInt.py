# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Pass asset parameter to solidity, asset integer type"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("asset_int")
@lcc.suite("Check scenario 'Parameter asset is integer type'")
class AssetInt(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("asset_int", "code")
        self.asset_balance = self.get_byte_code("asset_int", "assetbalance(address,uint64)")

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
    @lcc.test("The scenario describes the ability to pass an asset type integer, written in Solidity.")
    def asset_int_scenario(self):
        lcc.set_step("Create 'asset_int' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Get account balances using database_api")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        amount = response["result"][0]["amount"]
        if isinstance(amount, str):
            amount = int(amount)
        asset_id = response["result"][0]["asset_id"]
        lcc.log_info(
            "'get_account_balances' method return '{}' balance of '{}' account in '{}'".format(amount, self.echo_acc0,
                                                                                               asset_id))

        lcc.set_step("Call 'assetBalance' method")
        method_params = self.get_byte_code_param(self.echo_acc0) + self.get_byte_code_param(self.echo_asset)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.asset_balance + method_params,
                                                              callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Get contract output, asset balance")
        contract_output = self.get_contract_output(contract_result, output_type=int)
        lcc.log_info("Output: asset balance of '{}' account is '{}' in '{}'".format(self.echo_acc0, contract_output,
                                                                                    self.echo_asset))

        lcc.set_step("Check matching asset balances")
        check_that(
            "asset balances of '{}' account in '{}'".format(self.echo_acc0, self.echo_asset),
            contract_output,
            equal_to(amount),
        )
