# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, not_equal_to, check_that_in, has_entry, is_list, is_

from common.base_test import BaseTest

SUITE = {
    "description": "Checking the subscription to change objects in the network"
}


@lcc.suite("Subscription testing")
@lcc.hidden()
class SubscribeMethods(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info(
            "Database API identifiers is '{}'".format(self.__api_identifier))

    @lcc.test("Set subscribe callback. Param=True")
    def test_set_subscribe_callback_true(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        params = [subscription_callback_id, True]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set subscribe callback")
        check_that(
            "'subscribe callback'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Get notice and check information about the object with the results "
                     "of the implementation of contracts of the block")
        response_notice_new_block = self.get_notice(subscription_callback_id, object_id="1.18.")
        check_that(
            "''results_id' of a new block'",
            response_notice_new_block["results_id"],
            is_list(is_([])),
        )

        lcc.set_step("Get object '2.1.0'")
        param = "2.1.0"
        response_id = self.send_request(self.get_request("get_objects", [[param]]), self.__api_identifier)
        response = self.get_response(response_id)["result"][0]

        lcc.set_step("Subscription check for object updates '2.1.0'")
        object_keys = list(response)[:]
        self.get_notice(subscription_callback_id, object_id="1.18.")
        response_notice = self.get_notice(subscription_callback_id, object_id=param)

        lcc.set_step("Check object format")
        for j in range(len(response_notice)):
            check_that(
                "'updated object '{}''".format(param),
                response_notice,
                has_entry(
                    object_keys[j],
                ),
            )

        lcc.set_step("Check that updated object does not match previous")
        check_that_in(
            response_notice,
            "head_block_number", not_equal_to(response["head_block_number"]),
            "time", not_equal_to(response["time"]),
            "last_irreversible_block_num", not_equal_to(response["last_irreversible_block_num"]),
        )

        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that canceled all subscriptions")
        check_that(
            "'subscribe result'",
            response["result"],
            is_none(),
        )

    @lcc.test("Set subscribe callback. Param=False")
    def test_set_subscribe_callback_false(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        params = [subscription_callback_id, False]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set subscribe callback")
        check_that(
            "'subscribe callback'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Get object '2.1.0'")
        param = "2.1.0"
        response_id = self.send_request(self.get_request("get_objects", [[param]]), self.__api_identifier)
        response = self.get_response(response_id)["result"][0]

        lcc.set_step("Subscription check for object updates '2.1.0'")
        object_keys = list(response)[:]
        response_notice = self.get_notice(subscription_callback_id, object_id=param)

        lcc.set_step("Check object format")
        for j in range(len(response_notice)):
            check_that(
                "'updated object '{}''".format(param),
                response_notice,
                has_entry(
                    object_keys[j],
                ),
            )

        lcc.set_step("Check that updated object does not match previous")
        check_that_in(
            response_notice,
            "head_block_number", not_equal_to(response["head_block_number"]),
            "time", not_equal_to(response["time"]),
            "last_irreversible_block_num", not_equal_to(response["last_irreversible_block_num"]),
        )

        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that canceled all subscriptions")
        check_that(
            "'subscribe result'",
            response["result"],
            is_none(),
        )

    @lcc.test("Set block applied callback")
    def test_set_block_applied_callback(self, get_random_integer):
        lcc.set_step("Set block applied callback")
        subscription_callback_id = get_random_integer
        param = [subscription_callback_id]
        response_id = self.send_request(self.get_request("set_block_applied_callback", param),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set block applied callback")
        check_that(
            "'block applied callback'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Check new block hash number")
        response_notice = self.get_notice(subscription_callback_id)
        response_notice2 = self.get_notice(subscription_callback_id)
        check_that(
            "'blocks hash not match'",
            response_notice,
            not_equal_to(response_notice2),
        )

        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that canceled all subscriptions")
        check_that(
            "'subscribe result'",
            response["result"],
            is_none(),
        )

    @lcc.test("Set pending transaction callback")
    @lcc.hidden()
    def test_set_pending_transaction_callback(self):
        # todo: add a test when there will be operations
        pass

    @lcc.test("Subscribe to market")
    @lcc.hidden()
    def test_subscribe_to_market(self, callback, a, b):
        # todo: add a test when there will be operations
        pass

    @lcc.test("Unsubscribe to market")
    @lcc.hidden()
    def test_unsubscribe_from_market(self, a, b):
        # todo: add a test when there will be operations
        pass
