# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, this_dict, check_that_entry, is_str, is_list, is_integer, \
    require_that, require_that_in

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

SUITE = {
    "description": "Method 'get_contract_history'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("history_api", "get_contract_history")
@lcc.suite("Check work of method 'get_contract_history'", rank=1)
class GetContractHistory(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__history_api_identifier = self.get_identifier("history")
        self.contract_id = None

    def get_sidechain_contract(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        return self.get_response(response_id)["result"]["parameters"]["sidechain_config"]["echo_contract_id"]

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.contract_id = self.get_sidechain_contract()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_history'")
    # todo: change to run on an empty node.
    def method_main_check(self):
        stop = start = "1.11.0"
        limit = 5
        lcc.set_step("Get contract history")
        params = [self.contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check response from method 'get_contract_history'")
        result = response["result"]
        check_that(
            "'number of history results'",
            len(result), is_(limit)
        )
        for i in range(len(result)):
            list_operations = result[i]
            with this_dict(list_operations):
                if check_that_entry("id", is_str(), quiet=True):
                    if not self.validator.is_operation_history_id(list_operations["id"]):
                        lcc.log_error("Wrong format of operation id, got")
                check_that_entry("op", is_list(), quiet=True)
                check_that_entry("result", is_list(), quiet=True)
                check_that_entry("block_num", is_integer(), quiet=True)
                check_that_entry("trx_in_block", is_integer(), quiet=True)
                check_that_entry("op_in_trx", is_integer(), quiet=True)
                check_that_entry("virtual_op", is_integer(), quiet=True)


@lcc.prop("testing", "positive")
@lcc.tags("history_api", "get_contract_history")
@lcc.suite("Positive testing of method 'get_contract_history'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        self.echo_operations = EchoOperations()
        self.account_1 = "test-echo-1"
        self.account_2 = "test-echo-2"
        self.contract = self.get_byte_code("piggy_code")
        self.get_pennie = self.get_byte_code("piggy_getPennie")
        self.broadcast_result = None

    def add_balance_to_new_account(self, account, operation_count=1):
        lcc.log_info("Add balance to new account for contract operations")
        operation = self.echo_operations.get_create_contract_operation(echo=self.echo, registrar=account,
                                                                       bytecode=self.contract)
        fee = self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"]
        operation = self.echo_operations.get_call_contract_operation(echo=self.echo, registrar=account,
                                                                     bytecode=self.get_pennie, callee="1.16.0")
        fee = fee + (operation_count * self.get_required_fee(operation, self.__database_api_identifier)[0]["amount"])
        operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.account_1,
                                                                to_account_id=account, amount=fee)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        return self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

    def get_valid_contract_id(self, registrar, contract, value_amount=0):
        if registrar != self.account_1:
            self.broadcast_result = self.add_balance_to_new_account(registrar)
            if not self.is_operation_completed(self.broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(self.broadcast_result))
        operation = self.echo_operations.get_create_contract_operation(echo=self.echo, registrar=registrar,
                                                                       bytecode=contract, fee_amount=500,
                                                                       value_amount=value_amount)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=operation,
                                                          log_broadcast=False)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        contract_id_16 = self.get_trx_completed_response(response_id)
        return self.get_contract_id(contract_id_16)

    def fill_account_history_with_contract_transfer_operation(self, registrar, contract_id, operation_count):
        if registrar != self.account_1:
            self.broadcast_result = self.add_balance_to_new_account(registrar, operation_count)
            if not self.is_operation_completed(self.broadcast_result, expected_static_variant=0):
                raise Exception("Error: can't add balance to new account, response:\n{}".format(self.broadcast_result))
        operation = self.echo_operations.get_call_contract_operation(echo=self.echo, registrar=registrar,
                                                                     bytecode=self.get_pennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        if operation_count == 1:
            broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation,
                                                              log_broadcast=False)
            return broadcast_result
        list_operations = []
        for i in range(operation_count):
            list_operations.append(collected_operation)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=list_operations,
                                                          log_broadcast=False)
        return broadcast_result

    def call_get_contract_history(self, contract_id, stop, limit, start):
        lcc.log_info("Get '{}' account history".format(contract_id))
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        return self.get_response(response_id)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.account_1 = self.get_account_id(self.account_1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.account_2 = self.get_account_id(self.account_2, self.__database_api_identifier,
                                             self.__registration_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check contract history of new account")
    @lcc.depends_on("HistoryApi.GetContractHistory.GetContractHistory.method_main_check")
    def new_contract_history(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        stop = start = "1.11.0"
        limit = 100
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)

        lcc.set_step("Perform create contract operation")
        contract_id = self.get_valid_contract_id(new_account, self.contract)

        lcc.set_step("Get new account history")
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check new account history")
        check_that(
            "'new account history'",
            response["result"], is_list([])
        )

    @lcc.prop("type", "method")
    @lcc.test("Check limit number of operations to retrieve")
    @lcc.depends_on("HistoryApi.GetContractHistory.GetContractHistory.method_main_check")
    def limit_operations_to_retrieve(self, get_random_valid_account_name, get_random_integer_up_to_hundred):
        new_account = get_random_valid_account_name
        stop = start = "1.11.0"
        min_limit = 1
        max_limit = 100
        # todo: add 'get_random_integer_up_to_hundred' fixture to run on an empty node.
        call_contract_count = get_random_integer_up_to_hundred
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)

        lcc.set_step("Perform create contract operation")
        contract_id = self.get_valid_contract_id(new_account, self.contract, value_amount=max_limit)

        lcc.set_step("Perform operations using a new account. Call contract operation count equal to limit")
        self.fill_account_history_with_contract_transfer_operation(new_account, contract_id, call_contract_count)

        lcc.set_step(
            "Check that count of new contract history with the maximum limit is equal to call_contract_count")
        response = self.call_get_contract_history(contract_id, stop, max_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(call_contract_count)
        )

        lcc.set_step("Check minimum list length contract history")
        response = self.call_get_contract_history(contract_id, stop, min_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(min_limit)
        )

        lcc.set_step("Perform operations using a new account to create max_limit operations")
        self.fill_account_history_with_contract_transfer_operation(new_account, contract_id,
                                                                   max_limit - call_contract_count)

        lcc.set_step(
            "Check that count of new contract history with the limit = max_limit is equal to max_limit")
        response = self.call_get_contract_history(contract_id, stop, max_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(max_limit)
        )

    @lcc.prop("type", "method")
    @lcc.test("Check stop and start IDs of the operations in contract history")
    @lcc.depends_on("HistoryApi.GetContractHistory.GetContractHistory.method_main_check")
    def stop_and_start_operations(self, get_random_integer):
        value_amount = get_random_integer
        stop = "1.11.0"
        start = "1.11.0"
        contract_transfer_operation = self.echo_operations.get_operation_json("contract_transfer_operation",
                                                                              example=True)
        operations = []
        operation_ids = []

        lcc.set_step("Perform create contract operation")
        contract_id = self.get_valid_contract_id(self.account_1, self.contract, value_amount=value_amount)

        lcc.set_step("Perform one operation")
        operation_count = 1
        self.fill_account_history_with_contract_transfer_operation(self.account_1, contract_id, operation_count)
        contract_transfer_operation[1].update({"from": contract_id, "to": self.account_1})
        contract_transfer_operation[1]["amount"].update({"amount": 1})
        operations.append(contract_transfer_operation)

        limit = operation_count
        lcc.set_step("Get contract history. Limit: '{}'".format(limit))
        response = self.call_get_contract_history(contract_id, stop, limit, start)

        lcc.set_step("Check contract history to see added operation and store operation id")
        require_that(
            "'account history'",
            response["result"][0]["op"], is_list(operations[0])
        )
        operation_id = response["result"][0]["id"]

        lcc.set_step("Perform another operations")
        operation_count = 5
        self.fill_account_history_with_contract_transfer_operation(self.account_1, contract_id, operation_count)
        for i in range(operation_count):
            contract_transfer_operation[1].update({"from": contract_id, "to": self.account_1})
            contract_transfer_operation[1]["amount"].update({"amount": 1})
            operations.append(contract_transfer_operation)

        limit = operation_count
        stop = operation_id
        lcc.set_step("Get contract history. Stop: '{}', limit: '{}'".format(stop, limit))
        response = self.call_get_contract_history(contract_id, stop, limit, start)

        lcc.set_step("Check contract history to see added operations and store operation ids")
        operations.reverse()
        for i in range(limit):
            require_that(
                "'account history'",
                response["result"][i]["op"], is_list(operations[i])
            )
            operation_ids.append(response["result"][i]["id"])

        limit = operation_count + 1
        stop = operation_id
        start = operation_ids[0]
        lcc.set_step("Get contract history. Stop: '{}', limit: '{}' and start: '{}'".format(stop, limit, start))
        response = self.call_get_contract_history(contract_id, stop, limit, start)

        lcc.set_step("Check contract history to see operations from the selected ids interval")
        for i in range(len(response["result"])):
            lcc.log_info("Check operation #{}:".format(i))
            require_that_in(
                response["result"][i],
                ["id"], is_str(operation_ids[i]),
                ["op"], is_list(operations[i])
            )
