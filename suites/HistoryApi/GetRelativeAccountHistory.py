# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, this_dict, check_that_entry, is_str, is_list, is_integer, \
    require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_relative_account_history'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("history_api", "get_relative_account_history")
@lcc.suite("Check work of method 'get_relative_account_history'", rank=1)
class GetRelativeAccountHistory(BaseTest):

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
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc1))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_relative_account_history'")
    # todo: change to run on an empty node.
    def method_main_check(self):
        stop = start = 0
        limit = 1
        lcc.set_step("Get relative account history")
        params = [self.echo_acc1, stop, limit, start]
        response_id = self.send_request(self.get_request("get_relative_account_history", params),
                                        self.__history_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_relative_account_history' with: account='{}', stop='{}', limit='{}', start='{}' "
                     "parameters".format(self.echo_acc1, stop, limit, start))

        lcc.set_step("Check response from method 'get_relative_account_history'")
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
@lcc.tags("history_api", "get_relative_account_history")
@lcc.suite("Positive testing of method 'get_relative_account_history'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None

    def get_relative_account_history(self, account, stop, limit, start, negative=False):
        lcc.log_info("Get relative '{}' account history".format(account))
        params = [account, stop, limit, start]
        response_id = self.send_request(self.get_request("get_relative_account_history", params),
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
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc2 = self.get_account_id(self.echo_acc2, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc1, self.echo_acc2))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check new account history")
    @lcc.depends_on("HistoryApi.GetRelativeAccountHistory.GetRelativeAccountHistory.method_main_check")
    def new_account_history(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        stop = start = 0
        limit = 100
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get new account history")
        response = self.get_relative_account_history(new_account, stop, limit, start)

        lcc.set_step("Check new account history")
        check_that(
            "'new account history'",
            response["result"], is_list([])
        )

    @lcc.prop("type", "method")
    @lcc.test("Check limit number of operations to retrieve")
    @lcc.depends_on("HistoryApi.GetRelativeAccountHistory.GetRelativeAccountHistory.method_main_check")
    def limit_operations_to_retrieve(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name
        stop = start = 0
        min_limit = 1
        max_limit = 100
        # todo: add 'get_random_integer_up_to_hundred' fixture to run on an empty node.
        operation_count = 50
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Perform operations using a new account. Operation count equal to limit")
        self.utils.fill_account_history_with_transfer_operations(self, self.echo, new_account, self.echo_acc1,
                                                                 self.__database_api_identifier,
                                                                 operation_count=operation_count)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        lcc.set_step(
            "Check that count of new account history with the maximum limit is equal to operation_count")
        response = self.get_relative_account_history(new_account, stop, max_limit, start)
        check_that(
            "'number of history results'",
            # todo: remove '+ 2' ("account_create_operation" и 1 "transfer_operation: faucet") to run on an empty node.
            len(response["result"]), is_(operation_count + 2)
        )

        lcc.set_step("Check minimum list length account history")
        response = self.get_relative_account_history(new_account, stop, min_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(min_limit)
        )

        lcc.set_step("Perform operations using a new account to create max_limit operations")
        # todo: remove '- 2' ("account_create_operation" и 1 "transfer_operation: faucet") to run on an empty node.
        self.utils.fill_account_history_with_transfer_operations(self, self.echo, new_account, self.echo_acc1,
                                                                 self.__database_api_identifier,
                                                                 operation_count=max_limit - operation_count - 2)
        lcc.log_info(
            "Fill account history with '{}' number of transfer operations".format(max_limit - operation_count - 2))

        lcc.set_step(
            "Check that count of new account history with the limit = max_limit is equal to max_limit")
        response = self.get_relative_account_history(new_account, stop, max_limit, start)
        check_that(
            "'number of history results'",
            len(response["result"]), is_(max_limit)
        )

    @lcc.prop("type", "method")
    @lcc.test("Check stop and start IDs of the operations in account history")
    @lcc.tags("Bug: 'ECHO-699'")
    @lcc.depends_on("HistoryApi.GetRelativeAccountHistory.GetRelativeAccountHistory.method_main_check")
    def stop_and_start_operations(self, get_random_integer, get_random_integer_up_to_hundred):
        transfer_amount_1 = get_random_integer
        transfer_amount_2 = get_random_integer_up_to_hundred
        stop = 0
        start = 0
        operations = []
        operation_ids = []

        lcc.set_step("Perform one operation")
        operation_count = 1
        broadcast_result = self.utils.fill_account_history_with_transfer_operations(self, self.echo, self.echo_acc1,
                                                                                    self.echo_acc2,
                                                                                    self.__database_api_identifier,
                                                                                    transfer_amount=transfer_amount_1,
                                                                                    operation_count=operation_count)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        operations.append(broadcast_result["trx"]["operations"][0])

        limit = operation_count
        lcc.set_step("Get account history. Limit: '{}'".format(limit))
        response = self.get_relative_account_history(self.echo_acc1, stop, limit, start)

        lcc.set_step("Check account history to see added operation and store operation id")
        require_that(
            "'account history'",
            response["result"][0]["op"], is_list(operations[0])
        )

        lcc.set_step("Perform another operations")
        operation_count = 5
        broadcast_result = self.utils.fill_account_history_with_transfer_operations(self, self.echo, self.echo_acc1,
                                                                                    self.echo_acc2,
                                                                                    self.__database_api_identifier,
                                                                                    transfer_amount=transfer_amount_2,
                                                                                    operation_count=operation_count)
        lcc.log_info("Fill account history with '{}' number of transfer operations".format(operation_count))

        for i in range(operation_count):
            operations.append(broadcast_result["trx"]["operations"][i])

        limit = operation_count
        stop = 1
        lcc.set_step("Get account history. Stop: '{}', limit: '{}'".format(stop, limit))
        response = self.get_relative_account_history(self.echo_acc1, stop, limit, start)

        lcc.set_step("Check account history to see added operations and store operation ids")
        operations.reverse()
        for i in range(limit):
            require_that(
                "'account history'",
                response["result"][i]["op"], is_list(operations[i])
            )
            operation_ids.append(response["result"][i]["id"])

        # todo: don't work start param. Bug: "ECHO-699"
        # limit = operation_count + 1
        # stop = 1
        # start = operation_count
        # lcc.set_step("Get account history. Stop: '{}', limit: '{}' and start: '{}'".format(stop, limit, start))
        # response = self.call_get_relative_account_history(self.echo_acc1, stop, limit, start)
        #
        # lcc.set_step("Check account history to see operations from the selected ids interval")
        # for i in range(limit):
        #     lcc.log_info("Check operation #{}:".format(i))
        #     require_that_in(
        #         response["result"][i],
        #         ["id"], is_str(operation_ids[i]),
        #         ["op"], is_list(operations[i])
        #     )
