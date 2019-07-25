# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_, is_true

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_integer

SUITE = {
    "description": "Create 'piggy' contract,call 'piggy' contract's methods ('greet', 'getPennie', 'breakPiggy') \
                   and get balance"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("attempt_hello_world")
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

    def get_account_history(self, account, stop, limit, start):
        params = [account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        return self.get_response(response_id, log_response=True)

    def _get_contract_id(self, broadcast_result):
        get_contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        get_contract_address = get_contract_result["result"][1]["exec_res"]["new_address"]
        contract_id = "1.14." + str(int(get_contract_address[24:], 16))
        return contract_id

    def get_contract_operation_result(self, contract_id, method_bytecode):
        call_contract_operation = self.echo_ops.get_call_contract_operation(self.echo, registrar=self.echo_acc0,
                                                                            bytecode=method_bytecode,
                                                                            callee=contract_id)
        collected_operation = self.collect_operations(call_contract_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=True)
        contract_operation_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        return contract_operation_result

    def get_contract_balance_amount(self, contract_id):
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        contract_balance_amount = self.get_response(response_id)["result"][0]["amount"]
        return contract_balance_amount

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', history='{}'".format(self.__database_api_identifier,
                                                                                         self.__registration_api_identifier,
                                                                                         self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("AttemptHelloWorld", "main")
    def attempt_hello_world(self):
        amount = get_random_integer()
        expected_string = "Hello World!!!"

        lcc.set_step("Perform 'create contract' operation.")
        create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                registrar=self.echo_acc0,
                                                                                bytecode=self.contract_bytecode,
                                                                                value_amount=amount)
        collected_operation = self.collect_operations(create_contract_operation, self.__database_api_identifier)
        create_contract_broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                                   log_broadcast=True)
        created_contract_id = create_contract_broadcast_result["trx"]["operation_results"][0][1]

        lcc.set_step("Check create_contract_result_id format.")
        if not self.validator.is_contract_result_id(created_contract_id):
            lcc.log_error("Create_contract_result_id format is wrong.")
        else:
            lcc.log_info("Create_contract_result_id is '{}'".format(created_contract_id))

        lcc.set_step("Call 'get account history' operation")
        account_history_last_operation = \
            self.get_account_history(account=self.echo_acc0, stop="1.10.0", limit=1, start="1.10.0")["result"][0][
                "op"][1]

        lcc.set_step("Check that account history contains 'create contract' operation")
        last_operation = create_contract_broadcast_result["trx"]["operations"][0][1]
        if account_history_last_operation == last_operation:
            check_equal = True
        else:
            check_equal = False
        check_that("'Account history contains 'create contract' operation.'", check_equal, is_true())

        lcc.set_step("Get created contract id")
        created_contract_id = self._get_contract_id(create_contract_broadcast_result)
        lcc.log_info("Created contract id: '{}'".format(created_contract_id))

        lcc.set_step("Call 'get_contract_balances' operation")
        created_contract_balance_amount = self.get_contract_balance_amount(contract_id=created_contract_id)
        check_that("'Created contract balance is right'",
                   created_contract_balance_amount, equal_to(amount))

        lcc.set_step("Call method 'greet'")
        contract_method_response = self.get_contract_operation_result(contract_id=created_contract_id,
                                                                      method_bytecode=self.greet)

        lcc.set_step("Check result of method 'greet'")
        contract_method_output = self.get_contract_output(contract_method_response, output_type=str,
                                                          len_output_string=len(expected_string))
        check_that("'Result of method 'greet''", contract_method_output, is_(expected_string))

        lcc.set_step("Call method 'getPennie'")
        self.get_contract_operation_result(contract_id=created_contract_id,
                                           method_bytecode=self.get_pennie)

        lcc.set_step("Check implementation of method 'getPennie'")
        created_contract_balance_amount = self.get_contract_balance_amount(contract_id=created_contract_id)
        check_that("'Balance of contract had decreased by 1'", created_contract_balance_amount,
                   equal_to(amount - 1))

        lcc.set_step("Call method 'breakPiggy'")
        self.get_contract_operation_result(contract_id=created_contract_id,
                                           method_bytecode=self.break_piggy)

        lcc.set_step("Check result of method 'breakPiggy': contract balance")
        created_contract_balance_amount = self.get_contract_balance_amount(contract_id=created_contract_id)
        check_that("'Contract balance has decreased to zero'", created_contract_balance_amount, equal_to(0))

        lcc.set_step("Check result of method 'breakPiggy': method 'get_object'")
        response_id = self.send_request(self.get_request("get_objects", [[created_contract_id]]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        check_that("'Contract was destroyed'", result[0]["destroyed"], is_true())
