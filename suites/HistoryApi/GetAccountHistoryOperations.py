# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, this_dict, check_that_entry, is_str, is_list, is_integer, \
    require_that, require_that_in

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_history_operations'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("history_api", "get_account_history_operations")
@lcc.suite("Check work of method 'get_account_history_operations '", rank=1)
class GetAccountHistoryOperations(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_history_operations'")
    def method_main_check(self):
        operation_id = self.echo.config.operation_ids.ACCOUNT_CREATE
        start = stop = "1.10.0"
        limit = 1
        lcc.set_step("Get account history operations")
        params = [self.echo_acc0, operation_id, start, stop, limit]
        response_id = self.send_request(self.get_request("get_account_history_operations", params),
                                        self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'get_account_history_operations' with: account='{}', operation_id='{}', stop='{}', start='{}',"
            " limit='{}' parameters".format(self.echo_acc0, operation_id, stop, start, limit))

        lcc.set_step("Check response from method 'get_account_history_operations'")
        result = response["result"]
        check_that(
            "'number of history results'",
            len(result), is_(limit)
        )
        for i in range(len(result)):
            list_operations = result[i]
            check_that(
                "'operation id'",
                list_operations["op"][0], is_(operation_id)
            )
            with this_dict(list_operations):
                if not self.validator.is_operation_history_id(list_operations["id"]):
                    lcc.log_error("Wrong format of 'operation id', got: {}".format(list_operations["id"]))
                else:
                    lcc.log_info("'operation_id' has correct format: operation_history_id")
                check_that_entry("op", is_list(), quiet=True)
                check_that_entry("result", is_list(), quiet=True)
                check_that_entry("block_num", is_integer(), quiet=True)
                check_that_entry("trx_in_block", is_integer(), quiet=True)
                check_that_entry("op_in_trx", is_integer(), quiet=True)
                check_that_entry("virtual_op", is_integer(), quiet=True)


@lcc.prop("testing", "positive")
@lcc.tags("history_api", "get_account_history_operations")
@lcc.suite("Positive testing of method 'get_account_history_operations'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None

    def get_account_history_operations(self, account, operation_id, start, stop, limit, negative=False):
        lcc.log_info("Get '{}' account history".format(account))
        params = [account, operation_id, start, stop, limit]
        response_id = self.send_request(self.get_request("get_account_history_operations", params),
                                        self.__history_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check new account history")
    @lcc.depends_on("HistoryApi.GetAccountHistoryOperations.GetAccountHistoryOperations.method_main_check")
    def new_account_history(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        operation_id = 0
        start = stop = "1.10.0"
        limit = 100
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get new account history")
        response = self.get_account_history_operations(new_account, operation_id, start, stop, limit)

        lcc.set_step("Check new account history")
        check_that(
            "'new account history'",
            response["result"], is_list([])
        )

    @lcc.prop("type", "method")
    @lcc.test("Check operation_id parameter")
    @lcc.tags("Bug: 'ECHO-700'")
    @lcc.depends_on("HistoryApi.GetAccountHistoryOperations.GetAccountHistoryOperations.method_main_check")
    def operation_id_to_retrieve(self, get_random_valid_account_name, get_random_valid_asset_name):
        new_account = get_random_valid_account_name
        new_asset_name = get_random_valid_asset_name
        operation_count = 1
        transfer_operation_id = self.echo.config.operation_ids.TRANSFER
        create_asset_operation_id = 10
        stop = start = "1.10.0"
        # todo: change '2' to '100' . Bug: "ECHO-700"
        limit = 2
        lcc.set_step("Create and get new account. Add balance to pay for asset_create_operation fee")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        broadcast_result = self.utils.add_balance_for_operations(self, self.echo, new_account,
                                                                 self.__database_api_identifier,
                                                                 asset_name=new_asset_name,
                                                                 operation_count=operation_count)
        lcc.log_info("New Echo account created, account_id='{}, balance added".format(new_account))

        lcc.set_step("Check that transfer operation added to account history")
        if self.is_operation_completed(broadcast_result, expected_static_variant=0):
            response = self.get_account_history_operations(new_account, transfer_operation_id, start, stop, limit)
            check_that(
                "'number of history results'",
                len(response["result"]), is_(operation_count)
            )

        lcc.set_step("Perform asset create operation using a new account")
        operation = self.echo_ops.get_asset_create_operation(echo=self.echo, issuer=new_account,
                                                             symbol=new_asset_name)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Check that create asset operation added to account history")
        if self.is_operation_completed(broadcast_result, expected_static_variant=1):
            # todo: remove 'limit'. Bug: "ECHO-700"
            limit = 1
            response = self.get_account_history_operations(new_account, create_asset_operation_id, start, stop,
                                                           limit)
            check_that(
                "'number of history results'",
                len(response["result"]), is_(operation_count)
            )

    @lcc.prop("type", "method")
    @lcc.test("Check limit number of operations to retrieve")
    @lcc.depends_on("HistoryApi.GetAccountHistoryOperations.GetAccountHistoryOperations.method_main_check")
    def limit_operations_to_retrieve(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        operation_id = 0
        stop = start = "1.10.0"
        min_limit = 1
        # todo: change '6' to '100'. Bug: "ECHO-700"
        max_limit = 6
        # todo: change 'max_limit' to  'get_random_integer_up_to_hundred' fixture. Bug: "ECHO-700"
        operation_count = max_limit
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}".format(new_account))

        lcc.set_step("Perform operations using a new account. Operation count equal to limit")
        self.utils.perform_transfer_operations(self, self.echo, new_account, self.echo_acc0,
                                               self.__database_api_identifier, operation_count=operation_count)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        lcc.set_step(
            "Check that count of new account history with the maximum limit is equal to operation_count")
        response = self.get_account_history_operations(new_account, operation_id, start, stop, max_limit)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(operation_count)
        )

        lcc.set_step("Check minimum list length account history")
        response = self.get_account_history_operations(new_account, operation_id, start, stop, min_limit)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(min_limit)
        )

        lcc.set_step("Perform operations using a new account to create max_limit operations")
        max_limit = 100
        self.utils.perform_transfer_operations(self, self.echo, new_account, self.echo_acc0,
                                               self.__database_api_identifier,
                                               operation_count=max_limit - operation_count)
        lcc.log_info(
            "Fill account history with '{}' number of transfer operations".format(max_limit - operation_count))

        lcc.set_step(
            "Check that count of new account history with the limit = max_limit is equal to max_limit")
        response = self.get_account_history_operations(new_account, operation_id, start, stop, max_limit)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(max_limit)
        )

    @lcc.prop("type", "method")
    @lcc.test("Check stop and start IDs of the operations in account history")
    @lcc.depends_on("HistoryApi.GetAccountHistoryOperations.GetAccountHistoryOperations.method_main_check")
    def stop_and_start_operations(self, get_random_integer, get_random_integer_up_to_hundred):
        transfer_amount_1 = get_random_integer
        transfer_amount_2 = get_random_integer_up_to_hundred
        stop = "1.10.0"
        start = "1.10.0"
        operation_identifier = 0
        operations = []
        operation_ids = []

        lcc.set_step("Perform one operation")
        operation_count = 1
        broadcast_result = self.utils.perform_transfer_operations(self, self.echo, self.echo_acc0, self.echo_acc1,
                                                                  self.__database_api_identifier,
                                                                  transfer_amount=transfer_amount_1,
                                                                  operation_count=operation_count)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        operations.append(broadcast_result["trx"]["operations"][0])

        limit = operation_count
        lcc.set_step("Get account history. Limit: '{}'".format(limit))
        response = self.get_account_history_operations(self.echo_acc0, operation_identifier, start, stop, limit)

        lcc.set_step("Check account history to see added operation and store operation id")
        require_that(
            "'account history'",
            response["result"][0]["op"], is_list(operations[0])
        )
        operation_id = response["result"][0]["id"]

        lcc.set_step("Perform another operations")
        operation_count = 5
        broadcast_result = self.utils.perform_transfer_operations(self, self.echo, self.echo_acc0, self.echo_acc1,
                                                                  self.__database_api_identifier,
                                                                  transfer_amount=transfer_amount_2,
                                                                  operation_count=operation_count)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        for i in range(operation_count):
            operations.append(broadcast_result["trx"]["operations"][i])

        limit = operation_count
        stop = operation_id
        lcc.set_step("Get account history. Stop: '{}', limit: '{}'".format(stop, limit))
        response = self.get_account_history_operations(self.echo_acc0, operation_identifier, start, stop, limit)

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
        lcc.set_step("Get account history. Start: '{}', stop: '{}' and limit: '{}'".format(start, stop, limit))
        response = self.get_account_history_operations(self.echo_acc0, operation_identifier, start, stop, limit)

        lcc.set_step("Check account history to see operations from the selected ids interval")
        for i in range(len(response["result"])):
            lcc.log_info("Check operation #{}:".format(i))
            require_that_in(
                response["result"][i],
                ["id"], is_str(operation_ids[i]),
                ["op"], is_list(operations[i])
            )
