# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from time import strptime

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, check_that, has_length, is_true, equal_to, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_recent_transaction_by_id'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_recent_transaction_by_id")
@lcc.suite("Check work of method 'get_recent_transaction_by_id'", rank=1)
class GetRecentTransactionById(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

    def compare_objects(self, first_field, second_field, key=None):
        if isinstance(first_field, (list, dict)):
            if isinstance(first_field, list) and len(first_field):
                for key, elem in enumerate(first_field):
                    self.compare_objects(elem, second_field[key])
            elif isinstance(first_field, dict) and len(first_field):
                for key in list(first_field.keys()):
                    self.compare_objects(first_field[key], second_field[key], key)
        else:
            description = "list element"
            if key:
                description = "'{}'".format(key)
            check_that("{}".format(description), first_field, equal_to(second_field), quiet=True)

    @staticmethod
    def compare_datetimes(first_time, second_time):
        pattern = "%Y-%m-%dT%H:%M:%S"
        return strptime(first_time, pattern) > strptime(second_time, pattern)

    def get_expiration_time(self, seconds):
        pattern = "%Y-%m-%dT%H:%M:%S"
        now = self.get_datetime(global_datetime=True)
        expiration = datetime.strptime(now, pattern) + timedelta(seconds=seconds)
        return expiration.strftime(pattern)

    def get_last_block_time(self):
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"]["time"]

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_recent_transaction_by_id'")
    def method_main_check(self):
        lcc.set_step("Collect 'get_recent_transaction_by_id' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)

        lcc.log_info("Transfer operation: '{}'".format(str(transfer_operation)))

        lcc.set_step("Broadcast transaction that contains simple transfer operation to the ECHO network")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)

        expiration = self.get_expiration_time(30)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   expiration=expiration, log_broadcast=False)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        lcc.set_step("Get recent transaction by id (before it expire)")
        params = [broadcast_result["id"]]
        response_id = self.send_request(self.get_request("get_recent_transaction_by_id", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_recent_transaction_by_id' with transaction_id='{}' parameter".format(
            params))

        lcc.set_step("Compare transaction objects (broadcast_result, 'get_recent_transaction_by_id' method)")
        transaction_from_broadcast_result = broadcast_result["trx"]
        transaction_from_api_method = response["result"]
        require_that(
            "'transaction from broadcast result'",
            transaction_from_broadcast_result, has_length(8)
        )
        require_that(
            "'transaction from 'get_recent_transaction_by_id' method result'",
            transaction_from_api_method, has_length(7)
        )
        self.compare_objects(transaction_from_api_method, transaction_from_broadcast_result)

        lcc.set_step("Wait time for transaction expiration")
        while True:
            expiration_status = self.compare_datetimes(
                self.get_datetime(global_datetime=True),
                transaction_from_broadcast_result["expiration"]
            )
            if expiration_status:
                break

        lcc.set_step("Get recent transaction by id (after it expire)")
        while True:
            last_block_time = self.get_last_block_time()
            if self.compare_datetimes(last_block_time, expiration):
                lcc.log_info("Call method 'get_recent_transaction_by_id' with transaction_id='{}'".format(
                    params))
                response_id = self.send_request(self.get_request("get_recent_transaction_by_id", params),
                                                self.__database_api_identifier)
                response = self.get_response(response_id)

                lcc.set_step("Check 'get_recent_transaction_by_id' method result for expired transaction")
                require_that(
                    "'expired transaction result'",
                    response["result"], is_none()
                )

                break
            self.set_timeout_wait(wait_block_count=1)
