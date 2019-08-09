# -*- coding: utf-8 -*-
import math

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Testing work of counting 'gas_used'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("gas_used")
@lcc.suite("Check scenario 'GasUsed'")
class GasUsed(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy()")
        self.enough_fee_amount = 2000
        self.contract_create_id = None
        self.contract_call_id = None

    @staticmethod
    def get_default_fee(response, operation_id):
        all_fees = response.get("result").get("parameters").get("current_fees").get("parameters")
        for i in range(len(all_fees)):
            if all_fees[i][0] == operation_id:
                return all_fees[i][1]["fee"]
        raise Exception("No needed operation")

    @staticmethod
    def get_gas_price(response):
        gas_price = response.get("result").get("parameters").get("gas_price")
        return [gas_price["price"], gas_price["gas_amount"]]

    @staticmethod
    def get_gas_used(response):
        return response.get("result")[1].get("tr_receipt").get("gas_used")

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
        self.contract_create_id = self.echo.config.operation_ids.CONTRACT_CREATE
        self.contract_call_id = self.echo.config.operation_ids.CONTRACT_CALL
        lcc.log_info("Echo operation ids are: contract_create='{}', contract_call='{}'".format(self.contract_create_id,
                                                                                               self.contract_call_id))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario checks that gas_used is count correct.")
    def gas_used_scenario(self):
        lcc.set_step("Get default fee and gas_price in global properties")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        response = self.get_response(response_id)

        default_fee_for_contract_creation = self.get_default_fee(response, self.contract_create_id)
        default_fee_for_contract_call = self.get_default_fee(response, self.contract_call_id)
        gas_price = self.get_gas_price(response)[0]
        gas_amount = self.get_gas_price(response)[1]
        lcc.log_info(
            "Default fee for contract_creation: {}, default fee for contract_call: {}, "
            "gas_price: {}, gas_amount: {}".format(
                default_fee_for_contract_creation, default_fee_for_contract_call, gas_price, gas_amount))

        lcc.set_step("Get required fee for contract_create operation and store")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract)
        required_fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        lcc.log_info("Required fee for contract create: {}".format(required_fee))

        lcc.set_step("Create 'Piggy' contract in the Echo network. Store gas_used")
        self.add_fee_to_operation(operation, self.__database_api_identifier, fee_amount=self.enough_fee_amount)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        response = self.get_trx_completed_response(response_id)
        gas_used = self.get_gas_used(response)

        lcc.set_step("Check the correct amount of 'gas_used'")
        check_that(
            "'gas_used={}' for create contract counted correct".format(gas_used),
            required_fee,
            equal_to(math.ceil(gas_used / gas_amount * gas_price + default_fee_for_contract_creation))
        )

        lcc.set_step("Get required fee for contract_call operation and store")
        contract_id = self.get_contract_id(response)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy, callee=contract_id)
        required_fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        lcc.log_info("Required fee for call contract: {}".format(required_fee))

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method. Store gas_used")
        self.add_fee_to_operation(operation, self.__database_api_identifier, fee_amount=self.enough_fee_amount)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        response = self.get_trx_completed_response(response_id)
        gas_used = self.get_gas_used(response)

        lcc.set_step("Check the correct amount of 'gas_used'")
        check_that(
            "'gas_used={}' for call contract counted correct".format(gas_used),
            required_fee,
            equal_to(math.ceil(gas_used / gas_amount * gas_price + default_fee_for_contract_call))
        )
