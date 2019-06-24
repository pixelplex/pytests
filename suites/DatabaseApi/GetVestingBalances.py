# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_balance_objects'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_vesting_balances")
@lcc.suite("Check work of method 'get_vesting_balances'", rank=1)
class GetVestingBalances(BaseTest):

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
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_vesting_balances'")
    def method_main_check(self, get_random_integer):
        value_amount = get_random_integer
        lcc.set_step("Perform vesting balance create operation")
        operation = self.echo_ops.get_vesting_balance_create_operation(echo=self.echo, creator=self.echo_acc0,
                                                                       owner=self.echo_acc0, amount=value_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier, debug_mode=True)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        operation_result = self.get_operation_results_ids(broadcast_result)
        lcc.log_info("Vesting balance object '{}' created".format(operation_result))

        lcc.set_step("Get vesting balance of '{}' account".format(self.echo_acc0))
        response_id = self.send_request(self.get_request("get_vesting_balances", [self.echo_acc0]),
                                        self.__database_api_identifier, debug_mode=True)
        response = self.get_response(response_id, log_response=True)
