# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to, is_true
from common.base_test import BaseTest

SUITE = {
    "description": "Create two accounts, make transfer from 1st account to 2nd account, check 2nd account asset"
}


# @lcc.prop("create_transfer_asset", "main")
# @lcc.tags("Scenarios", "create_transfer_asset")
# @lcc.suite("Check scenario 'create_transfer_asset'")
class CreateTransferAsset(BaseTest):

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("CreateTransferAsset", "main")
    def main(self, get_random_valid_account_name, get_random_integer, get_random_valid_asset_name):
        account_count = 2
        account_names = [get_random_valid_account_name + str(i) for i in range(account_count)]
        account_ids = []
        private_keys = []
        random_amount = get_random_integer
        asset_id = "1.3.0"
        random_symbol = get_random_valid_asset_name

        lcc.set_step("Create two accounts")
        for i, account_name in enumerate(account_names):
            keys = self.generate_keys()
            public_key = keys[1]
            private_keys.append(keys[0])
            create_account_operation = self.echo_ops.get_account_create_operation(self.echo, account_name,
                                                                                  public_key,
                                                                                  public_key,
                                                                                  registrar=self.echo_acc0,
                                                                                  signer=self.echo_acc0)
            collected_operation = self.collect_operations(create_account_operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            created_account_id = self.get_operation_results_ids(broadcast_result)

            check_that("'Account #'{}' with id:'{}' is created'".format(str(i), created_account_id),
                       self.is_operation_completed(broadcast_result, expected_static_variant=1), is_true(), quiet=True)
            account_ids.append(created_account_id)

        lcc.set_step("Check that accounts made correctly.")
        for i in range(len(account_names)):
            response_account_by_name = self.send_request(self.get_request("get_account_by_name", [account_names[i]]),
                                                         self.__database_api_identifier)
            account_id = self.get_response(response_account_by_name)["result"]["id"]
            check_that("'Created account with id:'{}' was made correctly".format(account_id),
                       account_id, equal_to(account_ids[i]))

        lcc.set_step("Calculate fee for transfer and asset operations")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=account_ids[0],
                                                                  amount=0)
        transfer_fee = self.get_required_fee(transfer_operation, self.__database_api_identifier)[0]["amount"]
        lcc.log_info("Fee for transfer is '{}'".format(transfer_fee))
        create_asset_operation = self.echo_ops.get_asset_create_operation(echo=self.echo,
                                                                          issuer=account_ids[1],
                                                                          symbol=random_symbol,
                                                                          signer=private_keys[1])
        asset_fee = self.get_required_fee(create_asset_operation, self.__database_api_identifier)[0]["amount"]
        lcc.log_info("Fee for asset is '{}'".format(asset_fee))

        lcc.set_step("Transfer from main account to first account")
        amount_to_1st_account = random_amount + transfer_fee + asset_fee
        response_id = self.send_request(self.get_request("get_account_balances", [account_ids[0], [asset_id]]),
                                        self.__database_api_identifier)
        account1_amount_before_transfer = self.get_response(response_id)["result"][0]["amount"]
        response_id = self.send_request(self.get_request("get_account_balances", [self.echo_acc0, [asset_id]]),
                                        self.__database_api_identifier)
        main_account_amount_before_transfer = self.get_response(response_id)["result"][0]["amount"]

        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=account_ids[0],
                                                                  amount=amount_to_1st_account)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        check_that("Transfer from {} to {} was done.".format(self.echo_acc0, account_ids[0]),
                   self.is_operation_completed(broadcast_result, expected_static_variant=0), is_true())
        response_id = self.send_request(
            self.get_request("get_account_balances", [account_ids[0], [asset_id]]),
            self.__database_api_identifier)
        account1_amount_after_transfer = self.get_response(response_id)["result"][0][
            "amount"]
        response_id = self.send_request(
            self.get_request("get_account_balances", [self.echo_acc0, [asset_id]]),
            self.__database_api_identifier)
        main_account_amount_after_transfer = \
            self.get_response(response_id)["result"][0]["amount"]
        if (int(account1_amount_after_transfer) - int(account1_amount_before_transfer)) != amount_to_1st_account:
            lcc.log_error("Transfer is wrong, account {} got incorrect amount".format(account_ids[0]))
        elif (int(main_account_amount_before_transfer) - int(
                main_account_amount_after_transfer) - transfer_fee) != amount_to_1st_account:
            lcc.log_error("Transfer is wrong, account {} send incorrect amount".format(self.echo_acc0))
        else:
            lcc.log_info("Transfer is correct. {} got amount: {}, {} paid {} fee".format(account_ids[0],
                                                                                         amount_to_1st_account,
                                                                                         self.echo_acc0, transfer_fee))

        lcc.set_step("Transfer from 1st account to 2nd account")
        amount_to_2nd_account = amount_to_1st_account - transfer_fee
        response_account1_amount_id = self.send_request(
            self.get_request("get_account_balances", [account_ids[0], [asset_id]]),
            self.__database_api_identifier)
        account1_amount_before_transfer = \
            self.get_response(response_account1_amount_id)["result"][0]["amount"]
        response_account2_amount_id = self.send_request(
            self.get_request("get_account_balances", [account_ids[1], [asset_id]]),
            self.__database_api_identifier)
        account2_amount_before_transfer = \
            self.get_response(response_account2_amount_id)["result"][0]["amount"]
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=account_ids[0],
                                                                  to_account_id=account_ids[1],
                                                                  amount=amount_to_2nd_account, signer=private_keys[0],
                                                                  debug_mode=False)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        check_that("Transfer from {} to {} was done.".format(account_ids[0], account_ids[1]),
                   self.is_operation_completed(broadcast_result, expected_static_variant=0), is_true())
        response_account1_amount_id = self.send_request(
            self.get_request("get_account_balances", [account_ids[0], [asset_id]]),
            self.__database_api_identifier)
        account1_amount_after_transfer = \
            self.get_response(response_account1_amount_id)["result"][0]["amount"]
        response_account2_amount_id = self.send_request(
            self.get_request("get_account_balances", [account_ids[1], [asset_id]]),
            self.__database_api_identifier)
        account2_amount_after_transfer = \
            self.get_response(response_account2_amount_id)["result"][0]["amount"]

        if (int(account2_amount_after_transfer) - int(account2_amount_before_transfer)) != amount_to_2nd_account:
            lcc.log_error("Transfer is wrong, incorrect amount of account1")
        elif (int(account1_amount_before_transfer) - int(
                account1_amount_after_transfer) - transfer_fee) != amount_to_2nd_account:
            lcc.log_error("Transfer is wrong, incorrect amount of acc0")
        else:
            lcc.log_info(
                "Transfer is correct. {} got amount: {}, {} paid {} fee".format(account_ids[1], amount_to_2nd_account,
                                                                                account_ids[0], transfer_fee))

        lcc.set_step("Create 2nd account asset")
        create_asset_operation = self.echo_ops.get_asset_create_operation(echo=self.echo,
                                                                          issuer=account_ids[1],
                                                                          symbol=random_symbol,
                                                                          signer=private_keys[1], debug_mode=False)
        collected_operation = self.collect_operations(create_asset_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        check_that("Asset was created.", self.is_operation_completed(broadcast_result, expected_static_variant=1),
                   is_true())
        asset_id = broadcast_result["trx"]["operation_results"][0][1]
        response_asset = self.send_request(self.get_request("get_assets", [[asset_id, "1.3.0"]]),
                                           self.__database_api_identifier)
        account2_symbol = self.get_response(response_asset)["result"][0]["symbol"]
        if random_symbol != account2_symbol:
            lcc.log_error("Asset was created wrong")
        else:
            lcc.log_info("Asset was created right")
