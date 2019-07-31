# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_, check_that, is_list, equal_to, is_true

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_integer_up_to_ten

SUITE = {
    "description": "Scenario 'create contracts with cut bytecode'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("scenario", "create_contracts_with_cut_code")
@lcc.suite("Check work of scenario 'create_contracts_with_cut_code'", rank=1)
class CreateContractsWithCutCode(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        # todo: move to init
        self.contract_bytecode = self.get_byte_code("piggy", "code")
        self.get_pennie = self.get_byte_code("piggy", "getPennie")
        self.greet = self.get_byte_code("piggy", "greet")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy")

    def get_contract_balance_amount(self, contract_id):
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"][0]["amount"]

    def get_contract_operation_result(self, contract_id, method_bytecode):
        call_contract_operation = self.echo_ops.get_call_contract_operation(self.echo, registrar=self.echo_acc0,
                                                                            bytecode=method_bytecode,
                                                                            callee=contract_id)
        collected_operation = self.collect_operations(call_contract_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        return self.get_contract_result(broadcast_result, self.__database_api_identifier)

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

    @lcc.prop("type", "method")
    @lcc.test("Simple work of scenario 'create_contracts_with_cut_code'")
    def create_contracts_with_cut_code_scenario(self, get_random_integer):
        amount = get_random_integer
        num_1 = get_random_integer_up_to_ten()
        num_2 = get_random_integer_up_to_ten()

        expected_string = "Hello World!!!"


        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                value_amount=amount, bytecode=self.contract_bytecode)
        fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        cut_character_numbers = [num_1, -num_2]
        for cut_character_number in cut_character_numbers:

            lcc.set_step("Create contract with cut bytecode by '{}' character".format(cut_character_number))
            cut_contract_bytecode = self.contract_bytecode[cut_character_number:]
            operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                    value_amount=amount,
                                                                    bytecode=cut_contract_bytecode, fee_amount=fee)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=operation, log_broadcast=False)
            lcc.log_info("Contract result id '{}'".format(broadcast_result["trx"]["operation_results"][0][1]))

            lcc.set_step("Get contract result")
            status = True
            contract_result = None
            try:
                contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
            except Exception as e:
                lcc.log_info(str(e))
                if e == "Transaction not completed" or "StackUnderflow":
                    lcc.log_info("Wrong contract result")
                    status = False

            lcc.set_step("Get contract id")
            if status:
                contract_id = self.get_contract_id(contract_result)

                lcc.set_step("Get the contract by id")
                response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                                self.__database_api_identifier)
                response = self.get_response(response_id)
                lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(contract_id))

                lcc.set_step("Check simple work of method 'get_contract'")
                contract_type = response["result"][0]
                require_that("contract index", contract_type, is_(0))
                contract_info = response["result"][1]
                if not self.validator.is_hex(contract_info["code"]):
                    lcc.log_error("Wrong format of 'code', got: {}".format(contract_info["code"]))
                else:
                    lcc.log_info("'code' has correct format: hex")
                contract_storage = contract_info["storage"]
                if check_that("''storage' length'", len(contract_storage), is_(1)):
                    if not self.validator.is_hex(contract_storage[0][0]):
                        lcc.log_error(
                            "Wrong format of 'contract storage var 1', got: {}".format(contract_storage[0][0]))
                    else:
                        lcc.log_info("'contract storage var 1' has correct format: hex")
                    check_that("'contract storage var 2'", contract_storage[0][1], is_list(), quiet=True)

                lcc.set_step("Call contract method 'greet'")
                contract_method_response = self.get_contract_operation_result(contract_id=contract_id,
                                                                              method_bytecode=self.greet)

                lcc.set_step("Check contract method 'greet'")
                contract_method_output = self.get_contract_output(contract_method_response, output_type=str,
                                                                  len_output_string=len(expected_string))
                check_that("'Result of method 'greet''", contract_method_output, is_(expected_string))

                lcc.set_step("Call method 'getPennie'")
                self.get_contract_operation_result(contract_id=contract_id,
                                                   method_bytecode=self.get_pennie)

                lcc.set_step("Check implementation of method 'getPennie'")
                created_contract_balance_amount = self.get_contract_balance_amount(contract_id=contract_id)
                check_that("'Balance of contract had decreased by 1'", created_contract_balance_amount,
                           equal_to(amount - 1))

                lcc.set_step("Call method 'breakPiggy'")
                self.get_contract_operation_result(contract_id=contract_id,
                                                   method_bytecode=self.break_piggy)

                lcc.set_step("Check result of method 'breakPiggy': contract balance")
                created_contract_balance_amount = self.get_contract_balance_amount(contract_id=contract_id)
                check_that("'Contract balance has decreased to zero'", created_contract_balance_amount, equal_to(0))

                lcc.set_step("Check result of method 'breakPiggy': method 'get_object'")
                response_id = self.send_request(self.get_request("get_objects", [[contract_id]]),
                                                self.__database_api_identifier)
                result = self.get_response(response_id)["result"]
                check_that("'Contract was destroyed'", result[0]["destroyed"], is_true())
