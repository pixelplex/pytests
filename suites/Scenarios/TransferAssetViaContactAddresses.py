# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, require_that_entry, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Transfer assets using account addresses"
}


@lcc.prop("testing", "main")
@lcc.tags("transfer_asset_via_account_address")
@lcc.suite("Check scenario 'Transfer assets via account address'")
class TransferAssetViaContactAddresses(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def transfer_assets_to_account_address(self, address, transfer_amount):
        operation = self.echo_ops.get_transfer_to_address_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                                    to_address=address, amount=transfer_amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        self.is_operation_completed(broadcast_result, expected_static_variant=0)

    def get_account_balances(self, account):
        params = [account, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if len(result) > 0:
            for i in range(len(result)):
                if result[i]["asset_id"] == self.echo_asset or True:
                    return result[i]
        return result

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
    @lcc.test("The scenario describes the ability to transfer assets via account address recipient")
    def transfer_asset_via_account_address(self, get_random_valid_account_name, get_random_string,
                                           get_random_integer_up_to_hundred, get_random_integer_up_to_fifty):
        new_account = get_random_valid_account_name
        label = get_random_string
        addresses_count = 2
        account_address_object = []
        account_addresses = []
        transfer_amount = get_random_integer_up_to_hundred
        withdraw_amount = get_random_integer_up_to_fifty
        lcc.set_step("Create and get new account")
        new_account = self.get_account_id(new_account, self.__database_api_identifier,
                                          self.__registration_api_identifier)
        lcc.log_info("New Echo account created, account_id='{}'".format(new_account))

        lcc.set_step("Get account balance and store")
        balance_before_transfer = self.get_account_balances(new_account)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_before_transfer["amount"]))

        lcc.set_step("Create multiple account address for new account")
        for i in range(addresses_count):
            broadcast_result = self.utils.perform_account_address_create_operation(self, self.echo, new_account,
                                                                                   label + str(i),
                                                                                   self.__database_api_identifier)
            account_address_object.append(self.get_operation_results_ids(broadcast_result))

        # todo: change to 'get_account_addresses'. Bug: "ECHO-843"
        lcc.set_step("Get objects 'impl_account_address_object_type' and store addresses")
        for i in range(len(account_address_object)):
            param = [[account_address_object[i]]]
            response_id = self.send_request(self.get_request("get_objects", param), self.__database_api_identifier)
            account_addresses.append(self.get_response(response_id)["result"][0]["address"])

        lcc.set_step("Transfer assets via first account_address")
        self.transfer_assets_to_account_address(address=account_addresses[0], transfer_amount=transfer_amount)

        lcc.set_step("Get account balance after transfer and store")
        balance_after_transfer = self.get_account_balances(new_account)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_after_transfer["amount"]))

        lcc.set_step("Check that transfer assets completed successfully")
        with this_dict(balance_after_transfer):
            require_that_entry("amount", equal_to(balance_before_transfer["amount"] + transfer_amount))
            require_that_entry("asset_id", equal_to(balance_before_transfer["asset_id"]))

        lcc.set_step("Transfer assets via second account_address")
        amount = transfer_amount + transfer_amount
        self.transfer_assets_to_account_address(address=account_addresses[1], transfer_amount=amount)

        lcc.set_step("Get account balance after second transfer and store")
        balance_after_second_transfer = self.get_account_balances(new_account)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_after_second_transfer["amount"]))

        lcc.set_step("Check that second transfer assets completed successfully")
        with this_dict(balance_after_second_transfer):
            require_that_entry("amount", equal_to(balance_after_transfer["amount"] + amount))
            require_that_entry("asset_id", equal_to(balance_after_transfer["asset_id"]))

        lcc.set_step("Transfer assets received to account address")
        self.utils.perform_transfer_operations(self, self.echo, new_account, self.echo_acc0,
                                               self.__database_api_identifier, transfer_amount=withdraw_amount,
                                               only_in_history=False, log_broadcast=True)
        lcc.log_info("From the account of the recipient transferred assets to the account sender")

        lcc.set_step("Get account balance after return to sender")
        balance = self.get_account_balances(new_account)
        with this_dict(balance):
            require_that_entry("amount", equal_to(balance_after_second_transfer["amount"] - withdraw_amount))
            require_that_entry("asset_id", equal_to(balance_before_transfer["asset_id"]))

        lcc.set_step("Again transfer assets via first account_address")
        amount = transfer_amount + withdraw_amount
        self.transfer_assets_to_account_address(address=account_addresses[0], transfer_amount=amount)

        lcc.set_step("Get account balance after transfer and store")
        balance_after_transfer = self.get_account_balances(new_account)
        lcc.log_info("Account '{}' balance in '{}' asset: '{}'".format(new_account, self.echo_asset,
                                                                       balance_after_transfer["amount"]))

        lcc.set_step("Check that transfer assets completed successfully")
        with this_dict(balance_after_transfer):
            require_that_entry("amount", equal_to(balance["amount"] + amount))
            require_that_entry("asset_id", equal_to(balance_before_transfer["asset_id"]))
