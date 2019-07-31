# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_, is_false

from common.base_test import BaseTest
from fixtures.base_fixtures import get_random_integer_up_to_ten

SUITE = {
    "description": "Scenario 'create contracts with cut bytecode' fixed"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("scenario", "create_contracts_with_cut_code_fixed")
@lcc.suite("Check work of scenario 'create_contracts_with_cut_code_fixed'", rank=1)
class CreateContractsWithModifiedCodeFixed(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract_id = None
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

    @lcc.prop("type", "method")
    @lcc.test("Simple work of scenario 'create_contracts_with_cut_code_fixed'")
    def method_main_check(self, get_random_integer):
        amount = get_random_integer

        lcc.set_step("Create valid contract")
        contract_bytecode = self.get_byte_code("piggy", "code")
        operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                value_amount=amount, bytecode=contract_bytecode)
        fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                registrar=self.echo_acc0,
                                                                                value_amount=amount,
                                                                                bytecode=contract_bytecode,
                                                                                fee_amount=fee)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=create_contract_operation,
                                                   log_broadcast=False)
        result_id = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(
            self.get_request("get_contract_result", [result_id]),
            self.__database_api_identifier)
        response = self.get_response(response_id)
        valid_field_expected = response["result"][1]["exec_res"]["excepted"]
        valid_field_output = response["result"][1]["exec_res"]["output"]
        valid_field_new_address = response["result"][1]["exec_res"]["new_address"]
        contract_id = self.get_contract_id(response)
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        contract_response = self.get_response(response_id)
        valid_field_code = contract_response["result"][1]["code"]

        lcc.set_step("Create contract with cut bytecode")
        cut_contract_bytecodes = [contract_bytecode[get_random_integer_up_to_ten():],
                                  contract_bytecode[:-get_random_integer_up_to_ten()]]

        for cut_contract_bytecode in cut_contract_bytecodes:
            create_contract_operation = self.echo_ops.get_create_contract_operation(echo=self.echo,
                                                                                    registrar=self.echo_acc0,
                                                                                    value_amount=amount,
                                                                                    bytecode=cut_contract_bytecode,
                                                                                    fee_amount=fee)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=create_contract_operation,
                                                       log_broadcast=False)
            contract_id = self.get_operation_results_ids(broadcast_result)
            lcc.log_info("Created contact with id '{}'".format(contract_id))

            lcc.set_step("Check contract result of created contract with cut code by {} characters".format(
                int(len(contract_bytecode)) - int(len(cut_contract_bytecode))))
            response_id = self.send_request(
                self.get_request("get_contract_result", [contract_id]),
                self.__database_api_identifier)
            response = self.get_response(response_id)

            check_that("'Excepted'", response["result"][1]["exec_res"]["excepted"],
                       equal_to(valid_field_expected))
            check_that("'output'", response["result"][1]["exec_res"]["output"],
                       equal_to(valid_field_output))

            if response["result"][1]["exec_res"]["new_address"] != "0000000000000000000000000000000000000000":

                lcc.set_step("Get the contract by id")
                contract_id = self.get_contract_id(response, log_response=False)
                response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                                self.__database_api_identifier)
                contract_response = self.get_response(response_id)
                contract_info = contract_response["result"][1]

                check_that("'code'", contract_info["code"], equal_to(valid_field_code))
            else:
                check_that("'new_address'", response["result"][1]["exec_res"]["new_address"],
                           equal_to(valid_field_new_address))
