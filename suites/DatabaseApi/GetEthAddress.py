# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, this_dict, has_length, is_bool, check_that_entry

from common.base_test import BaseTest
from project import BLOCK_RELEASE_INTERVAL

SUITE = {
    "description": "Method 'get_eth_address'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_eth_address")
@lcc.suite("Check work of method 'get_eth_address'", rank=1)
class GetEthAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.temp_count = 0
        self.block_count = 10
        self.waiting_time_result = 0
        self.no_address = True

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_eth_address'")
    def method_main_check(self, get_random_valid_account_name):
        new_account = get_random_valid_account_name

        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get address of created account in the network")
        response_id = self.send_request(self.get_request("get_eth_address", [new_account]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_eth_address' of new account")

        lcc.set_step("Check simple work of method 'get_eth_address'")
        check_that(
            "'new account eth address'",
            response["result"],
            is_list([]), quiet=True
        )

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_generate_eth_address_operation(self, new_account, self.__database_api_identifier)

        lcc.set_step("Get updated ethereum address of created account in the network")
        while self.no_address:
            self.temp_count += 1
            response_id = self.send_request(self.get_request("get_eth_address", [new_account]),
                                            self.__database_api_identifier)
            response = self.get_response(response_id)
            if response["result"]:
                self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
                self.no_address = False
            if self.temp_count <= self.block_count:
                self.set_timeout_wait(BLOCK_RELEASE_INTERVAL, print_log=False)
                self.waiting_time_result = self.waiting_time_result + BLOCK_RELEASE_INTERVAL
        lcc.log_info(
            "Call method 'get_eth_address' of new account. Waiting time result='{}' seconds".format(
                self.waiting_time_result))

        lcc.set_step("Check new eth address in method 'get_eth_address'")
        result = response["result"][0]
        with this_dict(result):
            if check_that("account_eth_address", result, has_length(5)):
                if not self.validator.is_eth_address_id(result["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
                else:
                    lcc.log_info("'id' has correct format: eth_address_object_type")
                if not self.validator.is_account_id(result["acc_id"]):
                    lcc.log_error("Wrong format of 'acc_id', got: {}".format(result["acc_id"]))
                else:
                    lcc.log_info("'acc_id' has correct format: account_object_type")
                if not self.validator.is_hex(result["eth_addr"]):
                    lcc.log_error("Wrong format of 'eth_addr', got: {}".format(result["eth_addr"]))
                else:
                    lcc.log_info("'eth_addr' has correct format: hex")
                check_that_entry("is_approved", is_bool(), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)
                for i in range(len(result["approves"])):
                    if not self.validator.is_account_id(result["approves"][i]):
                        lcc.log_error("Wrong format of 'approver #{}', got: {}".format(i, result["acc_id"]))
                    else:
                        lcc.log_info("'approver #{}' has correct format: account_object_type".format(i))
