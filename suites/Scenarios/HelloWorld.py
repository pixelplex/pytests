# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, is_integer, is_str, check_that_in, is_true, this_dict, \
    check_that_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Testing contract creation and calling its methods"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("hello_world")
@lcc.suite("Check scenario 'Hello World'")
class HelloWorld(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.get_pennie = self.get_byte_code("piggy", "pennieReturned()")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy()")
        self.value_amount = 10

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
    @lcc.test("The scenario describes the mechanism of creating, deploying, "
              "and invoking a contract on the Echo network, written in Solidity.")
    def hello_world_scenario(self):
        expected_string = "Hello World!!!"

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract,
                                                                value_amount=self.value_amount,
                                                                value_asset_id=self.echo_asset)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Call 'greet' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Check get 'Hello World!!!'")
        contract_output = self.get_contract_output(contract_result, output_type=str,
                                                   len_output_string=len(expected_string))
        check_that("return of method 'greet'", contract_output, is_(expected_string))

        lcc.set_step("Get contract balance and store")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that_in(
            response["result"][0],
            "amount", is_integer(self.value_amount),
            "asset_id", is_str(self.echo_asset)
        )
        contract_balance = response["result"][0]["amount"]

        lcc.set_step("Get owner balance and store")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        with this_dict(response["result"][0]):
            self.check_uint64_numbers(response["result"][0], "amount")
            check_that_entry("asset_id", is_str(self.echo_asset))
        owner_balance = response["result"][0]["amount"]

        lcc.set_step("Call 'getPennie' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_pennie, callee=contract_id)
        fee = self.get_required_fee(operation, self.__database_api_identifier)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get contract. Amount should be reduced by one.")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that_in(
            response.get("result")[0],
            "amount", is_integer(contract_balance - 1),
            "asset_id", is_str(self.echo_asset)
        )

        lcc.set_step("Get owner balance. Amount should be reduced by fee and increase by one.")
        params = [self.echo_acc0, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        actual_balance = response.get("result")[0].get("amount")
        if isinstance(owner_balance, str):
            actual_balance = int(actual_balance)
            owner_balance = int(owner_balance)
        check_that(
            "'owner balance'",
            actual_balance,
            is_(owner_balance - fee[0].get("amount") + 1)
        )

        lcc.set_step("Destroy the contract. Call 'breakPiggy' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get contract balance, must be 0 (zero)")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'contract balance'",
            response["result"][0]["amount"],
            is_integer(0)
        )

        lcc.set_step("Check that contract to be 'destroyed=True'")
        response_id = self.send_request(self.get_request("get_objects", [[contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that(
            "contract deleted and 'destroyed'",
            response["result"][0]["destroyed"],
            is_true()
        )
