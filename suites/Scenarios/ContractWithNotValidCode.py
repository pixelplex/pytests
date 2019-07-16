# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError

from common.base_test import BaseTest

SUITE = {
    "description": "Testing contract creation with not hex format of contract code"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("not_valid_contract_code")
@lcc.suite("Check scenario 'Contract with not valid contract code'")
class ContractWithNotValidCode(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
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
    @lcc.test("The scenario describes the mechanism of creating contract with not hex format of contract code")
    def contract_with_not_valid_code_scenario(self, get_random_not_hex_string):
        not_hex_format_contract_code = get_random_not_hex_string

        lcc.set_step("Create contract in the Echo network with not hex format of contract code")
        try:
            operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                    bytecode=not_hex_format_contract_code)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            lcc.log_error(
                "Error: broadcast transaction complete. Contract created with cod: '{}'".format(
                    not_hex_format_contract_code))
        except RPCError as e:
            lcc.log_info(str(e))
