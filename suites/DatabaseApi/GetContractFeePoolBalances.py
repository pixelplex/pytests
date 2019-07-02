# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_fee_pool_balances'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_contract_fee_pool_balances")
@lcc.suite("Check work of method 'get_contract_fee_pool_balances '", rank=1)
class GetContractFeePoolBalances(BaseTest):

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
    @lcc.test("Simple work of method 'get_contract_fee_pool_balances'")
    def method_main_check(self, get_random_integer):
        value_to_poll = get_random_integer

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_poll,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pull added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Get a contract's fee pool balance")
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contract'")
        with this_dict(result):
            if check_that("contract pool balance", result, has_length(2)):
                check_that_entry("amount", is_(value_to_poll))
                check_that_entry("asset_id", is_(self.echo_asset))


