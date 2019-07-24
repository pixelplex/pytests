# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_, is_true

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
        self.contract_bytecode = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")
        self.get_pennie = self.get_byte_code("piggy", "getPennie")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy")

    def get_account_history(self, account, stop, limit, start, negative=False):
        params = [account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        return self.get_response(response_id, negative=negative)

    def _get_contract_id(self, broadcast_result):
        get_contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        get_contract_address = get_contract_result["result"][1]["exec_res"]["new_address"]
        contract_id = "1.14." + str(int(get_contract_address[24:], 16))
        return contract_id

    def call_contract_method(self, method_bytecode, contract_id):
        call_contract_operation = self.echo_ops.get_call_contract_operation(self.echo, registrar=self.echo_acc0,
                                                                            bytecode=method_bytecode,
                                                                            callee=contract_id)
        collected_operation = self.collect_operations(call_contract_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        return contract_result

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
        amount = 10000

        lcc.set_step("Call 'create contract' operation.")
        create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                registrar=self.echo_acc0,
                                                                                bytecode=self.contract_bytecode,
                                                                                value_amount=amount)
        collected_operation = self.collect_operations(create_contract_operation, self.__database_api_identifier)
        create_contract_broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                                   log_broadcast=True)

        lcc.set_step("Check 'create contract' operation.")
        created_contract_id = create_contract_broadcast_result["trx"]["operation_results"][0][1]
        if not self.validator.is_contract_result_id(created_contract_id):
            lcc.log_error("Contract result id is wrong.")
        else:
            lcc.log_info("Contract result id is '{}'".format(created_contract_id))
            lcc.log_info("Called 'create contract' operation.")

        lcc.set_step("Call 'get account history' operation")
        account_history_last_element = \
            self.get_account_history(account=self.echo_acc0, stop="1.10.0", limit=100, start="1.10.0")["result"][0][
                "op"][1]
        lcc.log_info("Account history last element: {}".format(account_history_last_element))

        lcc.set_step("Check that account history contains create account operation")
        last_operation = create_contract_broadcast_result["trx"]["operations"][0][1]
        check_that("'Account history contains 'create account' operation.'", account_history_last_element,
                   is_(last_operation), quiet=True)

        lcc.set_step("Get contract id")
        created_contract_id = self._get_contract_id(create_contract_broadcast_result)
        lcc.log_info("Contract id: '{}'".format(created_contract_id))

        lcc.set_step("Call 'get_contract_balances'")
        response_id = self.send_request(self.get_request("get_contract_balances", [created_contract_id]),
                                        self.__database_api_identifier)
        created_contract_balance_amount = self.get_response(response_id)["result"][0]["amount"]
        check_that("'Contract has correct balance'",
                   created_contract_balance_amount, equal_to(amount))

        lcc.set_step("Call method 'greet'")
        contract_method_response = self.call_contract_method(method_bytecode=self.greet,
                                                             contract_id=created_contract_id)
        lcc.log_info(str(contract_method_response))

        lcc.set_step("Check result of method 'greet'")
        expected_string = "Hello World!!!"
        contract_method_output = self.get_contract_output(contract_method_response, output_type=str,
                                                          len_output_string=len(expected_string))
        check_that("Result of method 'greet'", contract_method_output, is_("Hello World!!!"))

        lcc.set_step("Call method 'getPennie'")
        contract_method_response = self.call_contract_method(method_bytecode=self.get_pennie,
                                                             contract_id=created_contract_id)
        lcc.log_info(str(contract_method_response))

        lcc.set_step("Check implementation of method 'getPennie'")
        response_id = self.send_request(self.get_request("get_contract_balances", [created_contract_id]),
                                        self.__database_api_identifier)
        created_contract_balance_amount = self.get_response(response_id)["result"][0]["amount"]
        check_that("'Balance of contract had decreased by 1'", created_contract_balance_amount,
                   equal_to(amount - 1))
        contract_method_response = self.call_contract_method(method_bytecode=self.break_piggy,
                                                             contract_id=created_contract_id)
        lcc.log_info(str(contract_method_response))

        lcc.set_step("Check result of method 'breakPiggy")
        response_id = self.send_request(self.get_request("get_contract_balances", [created_contract_id]),
                                        self.__database_api_identifier)
        created_contract_balance_amount = self.get_response(response_id)["result"][0]["amount"]
        check_that("'Contract balance has decreased to zero'", created_contract_balance_amount, equal_to(0))
        response_id = self.send_request(self.get_request("get_objects", [[created_contract_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        check_that("'Contract was destroyed'", result[0]["destroyed"], is_true())
