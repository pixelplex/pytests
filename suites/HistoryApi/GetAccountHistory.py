# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, this_dict, check_that_entry, is_str, is_list, is_integer, \
    require_that, require_that_in

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

SUITE = {
    "description": "Method 'get_account_history'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("history_api", "get_account_history")
@lcc.suite("Check work of method 'get_account_history'", rank=1)
class GetAccountHistory(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        self.account = "test-echo-1"

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.account = self.get_account_id(self.account, self.__database_api_identifier,
                                           self.__registration_api_identifier)

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_history'")
    # todo: change to run on an empty node.
    def method_main_check(self):
        stop = start = "1.11.0"
        limit = 1
        lcc.set_step("Get account history")
        params = [self.account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check response from method 'get_account_history'")
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
                        lcc.log_error("Wrong format of operation id, got: {}".format(list_operations["id"]))
                check_that_entry("op", is_list(), quiet=True)
                check_that_entry("result", is_list(), quiet=True)
                check_that_entry("block_num", is_integer(), quiet=True)
                check_that_entry("trx_in_block", is_integer(), quiet=True)
                check_that_entry("op_in_trx", is_integer(), quiet=True)
                check_that_entry("virtual_op", is_integer(), quiet=True)


@lcc.prop("testing", "positive")
@lcc.tags("history_api", "get_account_history")
@lcc.suite("Positive testing of method 'get_account_history'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        self.echo_operations = EchoOperations()
        self.account_1 = "test-echo-1"
        self.account_2 = "test-echo-2"

    def add_balance_to_new_account(self, account, operation_count, transfer_amount):
        lcc.log_info("Add balance to new account for transfer operations")
        operation = self.echo_operations.get_operation_json("transfer_operation", example=True)
        fee = self.get_required_fee(operation, self.__database_api_identifier)
        amount = (operation_count * transfer_amount) + (operation_count * fee[0]["amount"])
        operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.account_1,
                                                                to_account_id=account, amount=amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        return self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)

    def fill_account_history_with_transfer_operations(self, account_1, account_2, operation_count, transfer_amount=1):
        add_balance_operation = 0
        if account_1 != self.account_1:
            broadcast_result = self.add_balance_to_new_account(account_1, operation_count, transfer_amount)
            if self.is_operation_completed(broadcast_result, expected_static_variant=0):
                add_balance_operation = 1
        operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=account_1,
                                                                to_account_id=account_2, amount=transfer_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        if operation_count == 1 or operation_count == 2:
            broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation,
                                                              log_broadcast=False)
            return broadcast_result
        list_operations = []
        for i in range(operation_count - add_balance_operation):
            list_operations.append(collected_operation)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=list_operations,
                                                          log_broadcast=False)
        return broadcast_result

    def call_get_account_history(self, account, stop, limit, start):
        lcc.log_info("Get '{}' account history".format(account))
        params = [account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
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
    @lcc.test("Check new account history")
    @lcc.depends_on("HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def new_account_history(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        stop = start = "1.11.0"
        limit = 100
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)

        lcc.set_step("Get new account history")
        params = [new_account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_account_history", params), self.__history_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check new account history")
        check_that(
            "'new account history'",
            response["result"], is_list([])
        )

    @lcc.prop("type", "method")
    @lcc.test("Check limit number of operations to retrieve")
    @lcc.depends_on("HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def limit_operations_to_retrieve(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        stop = start = "1.11.0"
        min_limit = 1
        max_limit = 100
        # todo: add 'get_random_integer_up_to_hundred' fixture to run on an empty node.
        operation_count = 50
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)

        lcc.set_step("Perform operations using a new account. Operation count equal to limit")
        self.fill_account_history_with_transfer_operations(new_account, self.account_1, operation_count)

        lcc.set_step(
            "Check that count of new account history with the maximum limit is equal to operation_count")
        response = self.call_get_account_history(new_account, stop, max_limit, start)
        check_that(
            "'number of history results'",
            # todo: remove '+ 3' ("account_create_operation" и 2 "transfer_operation: faucet") to run on an empty node.
            len(response["result"]), is_(operation_count + 3)
        )

        lcc.set_step("Check minimum list length account history")
        response = self.call_get_account_history(new_account, stop, min_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(min_limit)
        )

        lcc.set_step("Perform operations using a new account to create max_limit operations")
        # todo: remove '- 3' ("account_create_operation" и 2 "transfer_operation: faucet") to run on an empty node.
        self.fill_account_history_with_transfer_operations(new_account, self.account_1, max_limit - operation_count - 3)

        lcc.set_step(
            "Check that count of new account history with the limit = max_limit is equal to max_limit")
        response = self.call_get_account_history(new_account, stop, max_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(max_limit)
        )

    @lcc.prop("type", "method")
    @lcc.test("Check stop and start IDs of the operations in account history")
    @lcc.depends_on("HistoryApi.GetAccountHistory.GetAccountHistory.method_main_check")
    def stop_and_start_operations(self, get_random_integer, get_random_integer_up_to_hundred):
        transfer_amount_1 = get_random_integer
        transfer_amount_2 = get_random_integer_up_to_hundred
        stop = "1.11.0"
        start = "1.11.0"
        operations = []
        operation_ids = []

        lcc.set_step("Perform one operation")
        operation_count = 1
        broadcast_result_one_op = self.fill_account_history_with_transfer_operations(self.account_1, self.account_2,
                                                                                     operation_count,
                                                                                     transfer_amount_1)
        operations.append(broadcast_result_one_op["trx"]["operations"][0])

        limit = operation_count
        lcc.set_step("Get account history. Limit: '{}'".format(limit))
        response = self.call_get_account_history(self.account_1, stop, limit, start)

        lcc.set_step("Check account history to see added operation and store operation id")
        require_that(
            "'account history'",
            response["result"][0]["op"], is_list(operations[0])
        )
        operation_id = response["result"][0]["id"]

        lcc.set_step("Perform another operations")
        operation_count = 5
        broadcast_result_two_op = self.fill_account_history_with_transfer_operations(self.account_1, self.account_2,
                                                                                     operation_count,
                                                                                     transfer_amount_2)
        for i in range(operation_count):
            operations.append(broadcast_result_two_op["trx"]["operations"][i])

        limit = operation_count
        stop = operation_id
        lcc.set_step("Get account history. Stop: '{}', limit: '{}'".format(stop, limit))
        response = self.call_get_account_history(self.account_1, stop, limit, start)

        lcc.set_step("Check account history to see added operations and store operation ids")
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
        lcc.set_step("Get account history. Stop: '{}', limit: '{}' and start: '{}'".format(stop, limit, start))
        response = self.call_get_account_history(self.account_1, stop, limit, start)

        lcc.set_step("Check account history to see operations from the selected ids interval")
        for i in range(len(response["result"])):
            lcc.log_info("Check operation #{}:".format(i))
            require_that_in(
                response["result"][i],
                ["id"], is_str(operation_ids[i]),
                ["op"], is_list(operations[i])
            )
