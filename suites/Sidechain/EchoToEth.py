# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Withdraw ETH from the ECHO network to the ethereum wallet"
}


@lcc.prop("testing", "main")
@lcc.tags("eth_out")
@lcc.suite("Check scenario 'Ethereum out'")
class EchoToEth(BaseTest):

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

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario withdrawing assets from the echo account to the ethereum network")
    def ethereum_out_scenario(self):
        account = "1.2.106"
        eth_addr = "8973F8862269CA476dB468830A578a716Dfa8071"
        value = 1

        lcc.set_step("Get ethereum balance '{}'".format(account))
        ethereum_balance = self.utils.get_account_balances(self, account, self.__database_api_identifier,
                                                           self.eth_asset)

        # todo: ethereum steps

        lcc.set_step("Withdraw eth to ethereum address")
        broadcast_result = self.utils.perform_withdraw_eth_operation_operation(self, self.echo, account, eth_addr,
                                                                               value, self.__database_api_identifier,
                                                                               log_broadcast=True)

        lcc.set_step("Get ethereum balance '{}'".format(account))
        ethereum_balance = self.utils.get_account_balances(self, account, self.__database_api_identifier,
                                                           self.eth_asset)
