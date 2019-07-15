# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, is_list, check_that, has_length, is_true, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_proposed_transactions'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_proposed_transactions")
@lcc.suite("Check work of method 'get_proposed_transactions'", rank=1)
class GetProposedTransactions(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_proposed_transactions'")
    def method_main_check(self):
        lcc.set_step("Get proposed transactions for '{}' account".format(self.echo_acc0))
        response_id = self.send_request(self.get_request("get_proposed_transactions", [self.echo_acc0]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_proposed_transactions' with id='{}' parameter".format(self.echo_acc0))

        lcc.set_step("Check 'get_proposed_transactions' method result")
        require_that(
            "proposed transactions",
            response["result"], is_list([])
        )


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_proposed_transactions")
@lcc.suite("Positive testing of method 'get_proposed_transactions'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def get_expiration_time(self, seconds):
        pattern = "%Y-%m-%dT%H:%M:%S"
        now = self.get_datetime(global_datetime=True)
        expiration = datetime.strptime(now, pattern) + timedelta(seconds=seconds)
        return expiration.strftime(pattern)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        lcc.log_info("Registration API identifier is '{}'".format(self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Propose transaction using proposal_create operation and get info about it")
    @lcc.depends_on("DatabaseApi.GetProposedTransactions.GetProposedTransactions.method_main_check")
    def get_info_about_proposed_transaction(self):
        lcc.set_step("Send assets to '{}' account".format(self.echo_acc1))
        broadcast_result = self.utils.perform_transfer_operations(self, self.echo_acc0, self.echo_acc1,
                                                                  self.__database_api_identifier,
                                                                  transfer_amount=100000000)
        require_that(
            "broadcast transaction complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        lcc.set_step("Collect 'get_proposed_transactions' operation")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        lcc.set_step("Broadcast transaction that contains simple transfer operation to the ECHO network")
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        operations = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                             return_operations=True)
        proposal_create_operation = self.echo_ops.get_proposal_create_operation(
            echo=self.echo,
            fee_paying_account=self.echo_acc1,
            proposed_ops=operations,
            expiration_time=self.get_expiration_time(60)
        )
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=proposal_create_operation)
