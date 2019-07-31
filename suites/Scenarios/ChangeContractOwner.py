# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, equal_to, not_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Testing change contract owner"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("change_contract_owner")
@lcc.suite("Check scenario 'Change contract owner'")
class ChangeContractOwner(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.echo_acc2 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def get_contract_owner(self, contract_id):
        param = [contract_id]
        response_id = self.send_request(self.get_request("get_contracts", [param]), self.__database_api_identifier)
        return self.get_response(response_id)["result"][0]["owner"]

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
        self.echo_acc2 = self.get_account_id(self.accounts[2], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc1, self.echo_acc2))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes the mechanism of changing contract owner")
    def change_contract_owner_scenario(self):
        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Get info about created contract and store it owner")
        contract_owner = self.get_contract_owner(contract_id)
        require_that("'contract owner'", contract_owner, equal_to(self.echo_acc0))

        lcc.set_step("First: perform contract update operation to change contract owner")
        self.utils.perform_contract_update_operation(self, self.echo_acc0, contract_id, self.__database_api_identifier,
                                                     new_owner=self.echo_acc1)
        lcc.log_info("Contract owner changed from '{}' to '{}' successfully".format(self.echo_acc0, self.echo_acc1))

        lcc.set_step("Get updated info about created contract and check it new owner")
        updated_contract_owner_1 = self.get_contract_owner(contract_id)
        require_that("'updated contract owner'", updated_contract_owner_1, not_equal_to(contract_owner))
        require_that("'updated contract owner'", updated_contract_owner_1, equal_to(self.echo_acc1))

        lcc.set_step("Second: perform contract update operation to change contract owner again")
        self.utils.perform_contract_update_operation(self, self.echo_acc1, contract_id, self.__database_api_identifier,
                                                     new_owner=self.echo_acc2)
        lcc.log_info("Contract owner changed from '{}' to '{}' successfully".format(self.echo_acc1, self.echo_acc2))

        lcc.set_step("Get updated info about created contract and check it new owner")
        updated_contract_owner_2 = self.get_contract_owner(contract_id)
        require_that("'updated contract owner'", updated_contract_owner_2, not_equal_to(updated_contract_owner_1))
        require_that("'updated contract owner'", updated_contract_owner_2, equal_to(self.echo_acc2))
