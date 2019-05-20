# -*- coding: utf-8 -*-
import json

import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Testing work of 'sidechain'"
}


@lcc.prop("testing", "main")
@lcc.tags("sidechain")
# todo: add when will be added ethereum steps
@lcc.disabled()
@lcc.suite("Check scenario 'Sidechain'")
class Sidechain(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract_id = None
        # todo: get from global properties:
        self.eth_out = "6e20b99b"
        self.temp_count = 0

    def get_sidechain_config(self):
        response_id = self.send_request(self.get_request("get_global_properties"), self.__database_api_identifier)
        return self.get_response(response_id)["result"]["parameters"]["sidechain_config"]

    def get_echo_contract_id(self):
        return self.get_sidechain_config()["echo_contract_id"]

    def get_eth_contract_address(self):
        return self.get_sidechain_config()["eth_contract_address"]

    def get_withdraw_method_call(self, address):
        return self.eth_out + "000000000000000000000000" + address

    def get_withdraw_code(self, eth_address, transfer_id, value_amount):
        self.temp_count += 1
        # todo: delete lower(). Bug: "ECHO-660"
        response_id = self.send_request(self.get_request("get_sidechain_transfers", params=[eth_address.lower()]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        for i in range(len(response["result"])):
            # todo: change "transfer_id" to "id". Bug: "ECHO-669"
            if response["result"][i].get("transfer_id") == transfer_id and response["result"][i].get("amount") == str(
                    value_amount * pow(10, 12)):
                lcc.log_info(
                    "Sidechain transfer '{}':\n{}".format(transfer_id, json.dumps(response["result"][i], indent=4)))
                return response["result"][i].get("withdraw_code")
        if self.temp_count != 10:
            self.set_timeout_wait(30)
            return self.get_withdraw_code(eth_address, transfer_id, value_amount)
        raise Exception("No object with transfer id: '{}'".format(transfer_id))

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
        self.contract_id = self.get_echo_contract_id()
        lcc.log_info("Ethereum contract address: '{}'".format(self.get_eth_contract_address()))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.tags("eth_in")
    @lcc.test("The scenario checks work of sidechain in. Receive eETH to echo account")
    def sidechain_in(self):
        # todo: add manual steps. Send eth to echo_account
        lcc.set_step("Get account balance in eETH")
        params = [self.echo_acc0, [self.eeth_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.prop("type", "scenario")
    @lcc.tags("eth_out")
    @lcc.test("The scenario checks work of sidechain withdraw. Send eETH to ethereum wallet")
    def sidechain_out(self):
        lcc.set_step("Get withdraw bytecode")
        value_amount = 1
        eth_address = "2cf36df7b3e7f163833c572278e6adaec80c17d9"
        withdraw = self.get_withdraw_method_call(eth_address)

        # todo: add when will be added other steps
        # lcc.set_step("Get account balance in eETH")
        # params = [self.echo_acc0, [self.eeth_asset]]
        # response_id = self.send_request(self.get_request("get_account_balances", params),
        #                                 self.__database_api_identifier)
        # response = self.get_response(response_id, log_response=True)
        # eETH_registar = response["result"].get("amount")

        lcc.set_step("Call withdraw method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=withdraw, callee=self.contract_id,
                                                              value_amount=value_amount,
                                                              value_asset_id=self.eeth_asset)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)

        lcc.set_step("Get transfer id")
        transfer_id = self.get_transfer_id(contract_result)

        lcc.set_step("Get withdraw_code")
        withdraw_code = self.get_withdraw_code(eth_address, transfer_id, value_amount)
        lcc.log_info("Withdraw code for transfer_id '{}':\n{}".format(transfer_id, withdraw_code))
        # todo: add manual steps. Withdraw eth from echo_account

        # todo: add when will be added other steps
        # lcc.set_step("Check that the balance has decreased by the amount of withdrawal")
        # params = [self.echo_acc0, [self.eeth_asset]]
        # response_id = self.send_request(self.get_request("get_account_balances", params),
        #                                 self.__database_api_identifier)
        # response = self.get_response(response_id, log_response=True)
        # check_that(
        #     "account balance in eETH",
        #     response["result"].get("amount"), is_(eETH_registar - self.value_amount)
        # )
