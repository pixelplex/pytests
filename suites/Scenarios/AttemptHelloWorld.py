# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Create 'Hello World' scenario"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("Scenarios", "attempt_hello_world")
@lcc.suite("Create 'Hello World' scenario")
class AttemptHelloWorld(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None

    def get_account_history(self, account, stop, limit, start, negative=False):
        lcc.log_info("Get '{}' account history".format(account))
        params = [account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        return self.get_response(response_id, negative=negative)

    def convert_adress(self, number):
        contract_part = number[24:]
        return int(contract_part, 16)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.__history_api_identifier = self.get_identifier("history")
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("AttemptHelloWorld", "main")
    def attempt_hello_world(self):
        stop = start = "1.10.0"
        amount = 10000
        contract_bytecode = self.get_byte_code("piggy", "code")
        greet = self.get_byte_code("piggy", "greet")
        get_pennie = self.get_byte_code("piggy", "getPennie")
        break_piggy = self.get_byte_code("piggy", "breakPiggy")

        lcc.set_step("Create 'piggy' contract.")
        create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                registrar=self.echo_acc0,
                                                                                bytecode=contract_bytecode,
                                                                                value_amount=amount,
                                                                                )
        collected_operation = self.collect_operations(create_contract_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        check_that("'Operation is completed'", broadcast_result["trx"]["operation_results"][0][1][:5],
                   equal_to("1.15."))

        lcc.set_step("Get account history of registrar")
        account_history = self.get_account_history(account=self.echo_acc0, stop=stop, limit=100, start=start)

        lcc.set_step("Check that registrar account history contains create 'piggy' account operation")
        check_that("'Account history contains the operation.'", len(account_history["result"][0]["op"][1].keys()),
                   equal_to(6))

        lcc.set_step("Get 'piggy' contract id")
        get_contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        get_contract_code = get_contract_result["result"][1]["exec_res"]["output"]
        lcc.log_debug(str(get_contract_code))
        lcc.log_debug(str(contract_bytecode))
        get_contract_adress = get_contract_result["result"][1]["exec_res"]["new_address"]
        contract_id = "1.14." + str(self.convert_adress(get_contract_adress))
        lcc.log_info("'Piggy' contract id: '{}'".format(contract_id))

        lcc.set_step("Check 'piggy' contract id")
        # if check_that("Code of 'piggy' contract", str(get_contract_code), equal_to(str(contract_bytecode))):
        #     lcc.log_info("'Piggy' contract id: {}".format(contract_id))
        # else:
        #     lcc.log_error("Get wrong contract.")

        lcc.set_step("Get 'piggy' contract balance")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier, debug_mode=False)
        response = self.get_response(response_id, log_response=False)["result"][0]["amount"]
        lcc.log_info("'piggy' contract balance is '{}'".format(response))

        lcc.set_step("Check 'piggy' contract balance")
        check_that("'Amount of 'piggy' contract'", response, equal_to(amount))

        lcc.set_step("Calling method 'greet'")
        call_contract_operation = self.echo_ops.get_call_contract_operation(self.echo, registrar=self.echo_acc0,
                                                                            bytecode=greet, callee=contract_id,
                                                                            debug_mode=True)
        collected_operation = self.collect_operations(call_contract_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier, debug_mode=False)
        lcc.log_info("Called method 'greet' ")

        lcc.set_step("Check response of method 'greet'")
        expected_string = "Hello World!!!"
        contract_output = self.get_contract_output(contract_result, output_type=str,
                                                   len_output_string=len(expected_string))
        check_that("return of method 'greet'", contract_output, is_("Hello World!!!"))

        lcc.set_step("Calling the 'getPennie' method")
        call_contract_operation = self.echo_ops.get_call_contract_operation(self.echo, registrar=self.echo_acc0,
                                                                            bytecode=get_pennie, callee=contract_id)
        collected_operation = self.collect_operations(call_contract_operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        lcc.log_info("Called the 'getPennie' method")

        lcc.set_step("Check implementation of method 'getPennie'")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier, debug_mode=False)
        response = self.get_response(response_id, log_response=False)["result"][0]["amount"]
        check_that("'Amount of 'piggy' contract had decreased by 1'", response, equal_to(amount-1))

        lcc.set_step("Calling method 'breakPiggy'")
        call_contract_operation = self.echo_ops.get_call_contract_operation(self.echo, registrar=self.echo_acc0,
                                                                            bytecode=break_piggy, callee=contract_id,
                                                                            debug_mode=True)
        collected_operation = self.collect_operations(call_contract_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        lcc.log_info("Called method 'breakPiggy")

        lcc.set_step("Check result of method 'breakPiggy")






