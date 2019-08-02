# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_true, is_

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
        expected_string = "Hello World!!!"

        lcc.set_step("Create valid contract")
        create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                registrar=self.echo_acc0,
                                                                                value_amount=amount,
                                                                                bytecode=self.contract_bytecode)
        fee = self.get_required_fee(create_contract_operation, self.__database_api_identifier)[0]["amount"]
        create_contract_operation[1]["fee"].update({"amount": fee})
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=create_contract_operation,
                                                   log_broadcast=False)

        lcc.set_step("Get contract id")
        response_id = self.send_request(self.get_request("get_contract_result",
                                                         [self.get_operation_results_ids(broadcast_result)]),
                                        self.__database_api_identifier)
        contract_id = self.get_contract_id(self.get_response(response_id))

        response_id = self.send_request(self.get_request("get_contract", [contract_id]), self.__database_api_identifier)
        contract_response = self.get_response(response_id, log_response=True)
        valid_contract_type = contract_response["result"][0]
        valid_field_code = contract_response["result"][1]["code"]
        valid_field_storage_var1 = contract_response["result"][1]["storage"][0][0]
        valid_field_storage_var2 = contract_response["result"][1]["storage"][0][1]

        lcc.set_step("Create contract with cut bytecode")
        cut_bytecodes_of_contracts = [self.contract_bytecode[11:],
                                      self.contract_bytecode[:-9]]
        for cut_contract_bytecode in cut_bytecodes_of_contracts:
            create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                    registrar=self.echo_acc0,
                                                                                    value_amount=amount,
                                                                                    bytecode=cut_contract_bytecode,
                                                                                    fee_amount=fee)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=create_contract_operation,
                                                       log_broadcast=False)

            lcc.set_step("Call method 'get_contract_result' of cut contract")
            status = True
            contract_result = None
            try:
                contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
            except Exception as e:
                lcc.log_info(str(e))
                if e == "Transaction not completed" or "StackUnderflow":
                    lcc.log_info("Wrong contract result")
                    status = False
            if status:
                lcc.set_step("Get contract id")
                contract_id = self.get_contract_id(contract_result)

                lcc.set_step("Get the contract by id")
                response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                                self.__database_api_identifier)
                response = self.get_response(response_id)

                lcc.set_step(
                    "Check simple work of method 'get_contract' of contract with cut code by {} characters".format(
                        int(len(self.contract_bytecode)) - int(len(cut_contract_bytecode))))
                contract_type = response["result"][0]
                contract_info = response["result"][1]
                check_that("'contract_type'", contract_type, equal_to(valid_contract_type))
                check_that("'code'", contract_info["code"], equal_to(valid_field_code))
                if check_that("storage length", len(contract_info["storage"]),
                              equal_to(contract_response["result"][1]["storage"])):
                    check_that("'storage variable 1'", contract_info["storage"][0][0],
                               equal_to(valid_field_storage_var1))
                    check_that("'storage variable 2'", contract_info["storage"][0][1],
                               equal_to(valid_field_storage_var2))

                lcc.set_step("Call contract method 'greet'")
                contract_method_response = self.get_contract_operation_result(contract_id=contract_id,
                                                                              method_bytecode=self.greet)

                lcc.set_step("Check contract method 'greet'")
                contract_method_output = self.get_contract_output(contract_method_response, output_type=str,
                                                                  len_output_string=len(expected_string))
                check_that("'Result of method 'greet''", contract_method_output, is_(expected_string))

                lcc.set_step("Call method 'getPennie'")
                self.get_contract_operation_result(contract_id=contract_id, method_bytecode=self.get_pennie)

                lcc.set_step("Check implementation of method 'getPennie'")
                created_contract_balance_amount = self.get_contract_balance_amount(contract_id=contract_id)
                check_that("'Balance of contract had decreased by 1'", created_contract_balance_amount,
                           equal_to(amount - 1))

                lcc.set_step("Call method 'breakPiggy'")
                self.get_contract_operation_result(contract_id=contract_id, method_bytecode=self.break_piggy)

                lcc.set_step("Check result of method 'breakPiggy': contract balance")
                created_contract_balance_amount = self.get_contract_balance_amount(contract_id=contract_id)
                check_that("'Contract balance has decreased to zero'", created_contract_balance_amount, equal_to(0))

                lcc.set_step("Check result of method 'breakPiggy': method 'get_object'")
                response_id = self.send_request(self.get_request("get_objects", [[contract_id]]),
                                                self.__database_api_identifier)
                result = self.get_response(response_id)["result"]
                check_that("'Contract was destroyed'", result[0]["destroyed"], is_true())
