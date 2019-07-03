# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_list, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_pool_whitelist'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_contract_pool_whitelist")
@lcc.suite("Check work of method 'get_contract_pool_whitelist'", rank=1)
class GetContractPoolWhitelist(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")

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
    @lcc.test("Simple work of method 'get_contract_pool_whitelist'")
    def method_main_check(self, get_random_integer):
        value_to_pool = get_random_integer

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Get a contract's fee pool whitelist")
        response_id = self.send_request(self.get_request("get_contract_pool_whitelist", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contract_pool_whitelist'")
        with this_dict(result):
            if check_that("contract pool whitelist", result, has_length(2)):
                check_that_entry("whitelist", is_list([]))
                check_that_entry("blacklist", is_list([]))


@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_contract_pool_whitelist")
@lcc.suite("Negative testing of method 'get_contract_pool_whitelist'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")

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
    @lcc.test("Get whitelist of a contract that does not have a fee pool")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def whitelist_without_fee_pool(self):
        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Get a contract's pool whitelist. Fee pool not created")
        response_id = self.send_request(self.get_request("get_contract_pool_whitelist", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contract_pool_whitelist'")
        check_that("'get_contract_pool_whitelist' return error message", response, has_entry("error"), quiet=True)
