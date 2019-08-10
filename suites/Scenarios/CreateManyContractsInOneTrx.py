# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Creating many contracts in a single transaction"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("many_contracts_in_one_trx")
@lcc.suite("Check scenario 'Create many contracts in a single transaction'")
class CreateManyContractsInOneTrx(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.echo_acc0 = None

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

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario describes creating many contracts in a single transaction "
              "on the Echo network, written in Solidity.")
    def create_many_contracts_in_one_trx_scenario(self, get_random_integer_up_to_fifty):
        number_of_contracts = get_random_integer_up_to_fifty

        lcc.set_step("Create '{}' 'Piggy' contracts in the Echo network".format(number_of_contracts))
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        list_operations = []
        for i in range(number_of_contracts):
            list_operations.append(collected_operation)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations, log_broadcast=False)

        lcc.set_step("Check that all contracts created in the Echo network")
        check_that(
            "in 'broadcast_result' are 'operation_results'",
            len(broadcast_result.get("trx").get("operation_results")), equal_to(number_of_contracts)
        )
