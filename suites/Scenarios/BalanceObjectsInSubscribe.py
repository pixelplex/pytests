# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Comparison of objects balance accounts when transfer in subscription"
}


@lcc.prop("testing", "main")
@lcc.tags("balance_obj_in_subscription")
@lcc.suite("Check scenario 'Balance objects in subscription'")
class BalanceObjectsInSubscribe(BaseTest):

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
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "scenario")
    @lcc.test("The scenario comparing objects balance accounts when transfer assets")
    def compare_balance_objects_when_transfer(self, get_random_integer, get_random_integer_up_to_fifty):
        subscription_callback_id = get_random_integer
        transfer_amount = get_random_integer_up_to_fifty
        tracked_accounts = [self.echo_acc0, self.echo_acc1]
        accounts_balance_before_transfer = []
        accounts_balance_after_transfer = []

        lcc.set_step("Set subscribe callback")
        params = [subscription_callback_id, False]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        if self.get_response(response_id)["result"] is not None:
            raise Exception("Subscription failed")
        lcc.log_info("Global subscription turned on")

        lcc.set_step("Get accounts to subscribe to them")
        params = [[tracked_accounts[0], tracked_accounts[1]], True]
        response_id = self.send_request(self.get_request("get_full_accounts", params),
                                        self.__database_api_identifier)
        if not self.get_response(response_id)["result"]:
            raise Exception("Subscription failed")
        lcc.log_info("Accounts info received. Subscription completed")

        lcc.set_step("Get accounts balances before transfer and store")
        for i in range(len(tracked_accounts)):
            accounts_balance_before_transfer.append(
                self.utils.get_account_balances(self, tracked_accounts[i], self.__database_api_identifier)["amount"])
            lcc.log_info(
                "'{}' balance before transfer: '{}'".format(tracked_accounts[i], accounts_balance_before_transfer[i]))

        lcc.set_step("Transfer assets from account to account")
        broadcast_result = self.utils.perform_transfer_operations(self, tracked_accounts[0], tracked_accounts[1],
                                                                  self.__database_api_identifier,
                                                                  transfer_amount=transfer_amount)
        fee = broadcast_result["trx"]["operations"][0][1]["fee"]["amount"]
        lcc.log_info(
            "Transfer '{}' assets from '{}' to '{}'. Fee for operation: '{}'".format(transfer_amount,
                                                                                     tracked_accounts[0],
                                                                                     tracked_accounts[1], fee))

        lcc.set_step("Get notice about accounts updates")
        balance_object_count = 0
        notice = None
        requests_limit = 0
        wrong_notice = True
        while wrong_notice and requests_limit < 10:
            notice = self.get_notice(subscription_callback_id, notices_list=True)
            for i in range(len(notice)):
                if self.validator.is_account_balance_id(notice[i]["id"]):
                    wrong_notice = False
                requests_limit += 1
        for i in range(len(tracked_accounts)):
            for j in range(len(notice)):
                if notice[j]["owner"] == tracked_accounts[i]:
                    if self.validator.is_account_balance_id(notice[j]["id"]):
                        accounts_balance_after_transfer.append(notice[j]["balance"])
                        balance_object_count += 1
        if balance_object_count != len(tracked_accounts):
            raise Exception("Wrong notice received")
        lcc.log_info("Get notice with '{}' balance_objects owned by tracked accounts".format(balance_object_count))

        lcc.set_step("Check that the notice came the updated accounts balances")
        for i in range(len(tracked_accounts)):
            if i != 0:
                fee = 0
                transfer_amount = - transfer_amount
            check_that(
                "balance of account '{}'".format(tracked_accounts[i]),
                int(accounts_balance_after_transfer[i]),
                equal_to(int(accounts_balance_before_transfer[i]) - transfer_amount - fee)
            )
