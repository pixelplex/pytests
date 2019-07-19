# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to
from fixtures.base_fixtures import get_random_integer_up_to_hundred, get_random_integer, get_random_valid_asset_name
from common.base_test import BaseTest

SUITE = {
    "description": "Create two accounts, make transfer from 1st account to 2nd account, check 2nd account assert"
}


@lcc.prop("create two accounts", "main")
@lcc.tags("create_two_accounts")
@lcc.suite("Check scenario 'create two accounts'")
class ScenarioOne(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.amount = 1

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

    # @staticmethod
    # def get_valid_account_names(base_name, account_count):
    #     account_names = []
    #     for i in range(account_count):
    #         account_names.append(base_name + str(i))
    #     return account_names

    @lcc.tags("qa")
    @lcc.test("Create two accounts", "main")
    def main(self, get_random_valid_account_name):
        account_count = 2
        account_names = [get_random_valid_account_name + str(i) for i in range(account_count)]
        account_ids = []
        private_keys = []
        for account_name in account_names:
            keys = self.generate_keys()
            public_key = keys[1]
            private_key = keys[0]

            lcc.set_step("Create account '{}'".format(account_name))
            create_account_operation = self.echo_ops.get_account_create_operation(self.echo, account_name, public_key,
                                                                                  public_key,
                                                                                  registrar=self.echo_acc0,
                                                                                  signer=self.echo_acc0)
            collected_operation = self.collect_operations(create_account_operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
                raise Exception("Account is not created")
            operation_result = self.get_operation_results_ids(broadcast_result)
            lcc.log_info("Account is created, id='{}'".format(operation_result))

            lcc.set_step("Check that account with name '{}' made correctly.".format(account_name))
            account_id_from_broadcast_result = broadcast_result["trx"]["operation_results"][0][1]
            response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                            self.__database_api_identifier)
            account_id = self.get_response(response_id)["result"]["id"]
            if account_id != account_id_from_broadcast_result:
                lcc.log_error("Account '{}' is wrong".format(account_id_from_broadcast_result))
            else:
                lcc.log_info("Account '{}' is correct".format(account_id_from_broadcast_result))
            account_ids.append(account_id)
            private_keys.append(private_key)

        lcc.set_step("Transfer from echo_acc0 to 1st account")
        amount = get_random_integer() + 500
        asset_id = "1.3.0"
        account_id = account_ids[0]
        response_account1_amount_id = self.send_request(
            self.get_request("get_account_balances", [account_id, [asset_id]]),
            self.__database_api_identifier)
        account1_amount_before_transfer = \
        self.get_response(response_account1_amount_id)["result"][0]["amount"]
        response_echo_acc0_amount_id = self.send_request(
            self.get_request("get_account_balances", [self.echo_acc0, [asset_id]]),
            self.__database_api_identifier)
        echo_acc0_amount_before_transfer = \
            self.get_response(response_echo_acc0_amount_id)["result"][0]["amount"]
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=account_id,
                                                                  amount=amount)
        fee_amount = self.get_required_fee(transfer_operation, self.__database_api_identifier)[0]["amount"]
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Account is not created")
        else:
            lcc.log_info("Transfer was done: from {} to {}, amount = {}".format(self.echo_acc0, account_id, amount))
        lcc.log_debug(str(fee_amount))
        response_account1_amount_id = self.send_request(
            self.get_request("get_account_balances", [account_id, [asset_id]]),
            self.__database_api_identifier)
        account1_amount_after_transfer = self.get_response(response_account1_amount_id)["result"][0][
            "amount"]
        response_echo_acc0_amount_id = self.send_request(
            self.get_request("get_account_balances", [self.echo_acc0, [asset_id]]),
            self.__database_api_identifier)
        echo_acc0_amount_after_transfer = \
            self.get_response(response_echo_acc0_amount_id)["result"][0]["amount"]
        if (int(account1_amount_after_transfer) - int(account1_amount_before_transfer)) != amount:
            lcc.log_error("Transfer is wrong, incorrect amount of account1")
        elif (int(echo_acc0_amount_before_transfer) - int(echo_acc0_amount_after_transfer) - fee_amount) != amount:
            lcc.log_error("Transfer is wrong, incorrect amount of acc0")
        else:
            lcc.log_info("Transfer is correct. Account1 got amount: {}, fee is '{}' ".format(amount, fee_amount))
        account_ids.append(account_id)

        lcc.set_step("Transfer from 1st account to 2nd account")
        amount = amount-fee_amount-1

        account1_id = account_ids[0]
        account2_id = account_ids[1]

        response_account1_amount_id = self.send_request(
            self.get_request("get_account_balances", [account1_id, [asset_id]]),
            self.__database_api_identifier)
        account1_amount_before_transfer = \
            self.get_response(response_account1_amount_id)["result"][0]["amount"]
        response_account2_amount_id = self.send_request(
            self.get_request("get_account_balances", [account2_id, [asset_id]]),
            self.__database_api_identifier)
        account2_amount_before_transfer = \
            self.get_response(response_account2_amount_id)["result"][0]["amount"]
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=account1_id,
                                                                  to_account_id=account2_id,
                                                                  amount=amount, signer=private_keys[0])

        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("Account is not created")
        else:
            lcc.log_info("Transfer was done: from {} to {}, amount = {}".format(self.echo_acc0, account_id, amount))
        fee_amount = self.get_required_fee(transfer_operation, self.__database_api_identifier)[0][
            "amount"]
        response_account1_amount_id = self.send_request(
            self.get_request("get_account_balances", [account1_id, [asset_id]]),
            self.__database_api_identifier)
        account1_amount_after_transfer = \
            self.get_response(response_account1_amount_id)["result"][0]["amount"]
        response_account2_amount_id = self.send_request(
            self.get_request("get_account_balances", [account2_id, [asset_id]]),
            self.__database_api_identifier)
        account2_amount_after_transfer = \
            self.get_response(response_account2_amount_id)["result"][0]["amount"]
        if (int(account2_amount_after_transfer) - int(account2_amount_before_transfer)) != amount:
            lcc.log_error("Transfer is wrong, incorrect amount of account1")
        elif (int(account1_amount_before_transfer) - int(account1_amount_after_transfer) - fee_amount) != amount:
            lcc.log_error("Transfer is wrong, incorrect amount of acc0")
        else:
            lcc.log_info("Transfer is correct. Account1 got amount: {}, fee is '{}' ".format(amount, fee_amount))
        account_ids.append(account_id)

        lcc.set_step("Create account2 asset")
        random_symbol = get_random_valid_asset_name()
        lcc.log_debug(str(random_symbol))
        create_asset_operation = self.echo_ops.get_asset_create_operation(echo=self.echo,
                                                                          issuer=account2_id,
                                                                          symbol=random_symbol,
                                                                          signer=private_keys[1])
        collected_operation = self.collect_operations(create_asset_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=1):
            raise Exception("Asset was not created")
        else:
            lcc.log_info("Asset was done: from {} to {}, amount = {}".format(self.echo_acc0, account_id, amount))
        asset_id = broadcast_result["trx"]["operation_results"][0][1]
        response_asset = self.send_request(self.get_request("get_assets", [[asset_id, "1.3.0"]]),
                                        self.__database_api_identifier)
        account2_symbol = self.get_response(response_asset)["result"][0]["symbol"]
        if random_symbol != account2_symbol:
            lcc.log_error("Asset was created wrong, symbol is incorrect.")
        else:
            lcc.log_info("Account2 asset was created right, symbol is '{}'".format(account2_symbol))
        account_ids.append(account_id)



