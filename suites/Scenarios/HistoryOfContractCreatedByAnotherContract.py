# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, check_that_in, is_integer, is_str, require_that, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Use the contract to create a new contact and see its history"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("history_of_contract_created_by_another_contract")
@lcc.suite("Check scenario 'Contract history that was created using another contract'")
class HistoryOfContractCreatedByAnotherContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("contract_create_contract", "code")
        self.deploy_contract = self.get_byte_code("contract_create_contract", "deploy_contract()")
        self.get_creator = self.get_byte_code("contract_create_contract", "created_contract")["creator()"]
        self.tr_asset_to_creator = self.get_byte_code("contract_create_contract", "created_contract")[
            "tr_asset_to_creator()"]

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info("API identifiers are: database='{}', registration='{}', "
                     "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                           self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes the creation of a contract whose method creates a new contract. "
              "Getting the history of the created contract")
    @lcc.tags("Bug ECHO-812")
    def history_of_contract_created_by_another_contract(self):
        operations = []
        # todo: add. Bug ECHO-812
        # contract_create_operation = self.echo_ops.get_operation_json("contract_create_operation", example=True)
        contract_transfer_operation = self.echo_ops.get_operation_json("contract_transfer_operation", example=True)

        lcc.set_step("Create 'contract_contract_create' contract in the Echo network")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_id = self.get_contract_id(contract_result)

        lcc.set_step("Call 'deploy_contract' method")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.deploy_contract, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Add contract create operation")
        # todo: add. Bug ECHO-812
        # contract_create_operation.update()

        lcc.set_step("Get output with address of deployed contract")
        created_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(created_contract_id))

        lcc.set_step("Call 'get_creator' method of created contract")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_creator, callee=created_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        operations.insert(0, collected_operation[0][:-1])
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Get output with address of contract creator")
        creator_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(creator_contract_id))

        lcc.set_step("Check that the correct address of the contract creator is in the response")
        check_that(
            "contract address of contract creator in output",
            creator_contract_id,
            equal_to(contract_id),
        )

        lcc.set_step("Call 'tr_asset_to_creator' method of created contract")
        value_amount = 1
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.tr_asset_to_creator,
                                                              callee=created_contract_id, value_amount=value_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        operations.insert(0, collected_operation[0][:-1])
        contract_transfer_operation[1].update({"from": created_contract_id, "to": contract_id})
        contract_transfer_operation[1]["amount"].update({"amount": value_amount})
        operations.insert(0, contract_transfer_operation)

        lcc.set_step("Get contract balance and store")
        response_id = self.send_request(self.get_request("get_contract_balances", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        check_that_in(
            response["result"][0],
            "amount", is_integer(value_amount),
            "asset_id", is_str(self.echo_asset)
        )
        contract_balance = response["result"][0]["amount"]

        lcc.set_step("Check that contract creator received assets from created contract")
        check_that(
            "balance of contract creator",
            contract_balance,
            equal_to(value_amount),
        )

        lcc.set_step("Get contract history of created contract by another contract")
        stop, start = "1.6.0", "1.6.0"
        limit = 100
        params = [created_contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Get '{}' contract history".format(created_contract_id))

        # todo: add. Bug ECHO-812
        lcc.set_step("Check history of contract that created by another contract")
        for i in range(len(operations)):
            lcc.log_info("Check operation #{}:".format(i))
            require_that(
                "'contract history'",
                response["result"][i]["op"], is_list(operations[i])
            )
