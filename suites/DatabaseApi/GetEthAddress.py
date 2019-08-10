# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_list, this_dict, has_length, is_bool, check_that_entry, is_none

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_eth_address'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_eth_address")
@lcc.suite("Check work of method 'get_eth_address'", rank=1)
class GetEthAddress(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.temp_count = 0
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
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

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
        lcc.log_info("Call method 'get_eth_address' of new account '{}'".format(new_account))

        lcc.set_step("Check simple work of method 'get_eth_address'")
        check_that("'new account eth address'", response["result"], is_none(), quiet=True)

        lcc.set_step("Generate ethereum address for new account")
        self.utils.perform_sidechain_eth_create_address_operation(self, new_account, self.__database_api_identifier)
        lcc.log_info("Ethereum address generated successfully")

        lcc.set_step("Get updated ethereum address of created account in the network")
        eth_account_address = self.utils.get_eth_address(self, new_account,
                                                         self.__database_api_identifier)["result"]["eth_addr"]
        lcc.log_info("Ethereum address of '{}' account is '{}'".format(new_account, eth_account_address))

        lcc.set_step("Check new eth address in method 'get_eth_address'")
        response_id = self.send_request(self.get_request("get_eth_address", [new_account]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        with this_dict(result):
            if check_that("account_eth_address", result, has_length(6)):
                if not self.validator.is_eth_address_id(result["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(result["id"]))
                else:
                    lcc.log_info("'id' has correct format: eth_address_object_type")
                if not self.validator.is_account_id(result["account"]):
                    lcc.log_error("Wrong format of 'account', got: {}".format(result["account"]))
                else:
                    lcc.log_info("'account' has correct format: account_object_type")
                if not self.validator.is_hex(result["eth_addr"]):
                    lcc.log_error("Wrong format of 'eth_addr', got: {}".format(result["eth_addr"]))
                else:
                    lcc.log_info("'eth_addr' has correct format: hex")
                check_that_entry("is_approved", is_bool(), quiet=True)
                check_that_entry("approves", is_list(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)
