# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Entering the currency ERC20 token in the network ECHO to the account and withdraw that currency"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("sidechain_erc20")
@lcc.suite("Check scenario 'ERC20ToEcho and ERC20FromEchoToEth'")
class ERC20(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_ganache_ethereum()
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

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario checks the main parts before testing the ERC20 sidechain functionality")
    def erc20_sidechain_pre_run_scenario(self):
        pass
