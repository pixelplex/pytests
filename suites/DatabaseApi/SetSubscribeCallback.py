# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, is_list, is_, has_entry, check_that_in, not_equal_to, \
    require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'set_subscribe_callback'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("set_subscribe_callback")
@lcc.suite("Check work of method 'set_subscribe_callback'", rank=1)
class SetSubscribeCallback(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'set_subscribe_callback'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        params = [subscription_callback_id, True]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set subscribe callback")
        check_that(
            "'subscribe callback'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Get notice and check results id of the new block")
        response_notice_new_block1 = self.get_notice(subscription_callback_id, object_id="1.{}.".format(
            self.echo.config.object_types.block_result))
        check_that(
            "''results_id' of a new block'",
            response_notice_new_block1["results_id"],
            is_list(is_([])),
        )

        lcc.set_step("Get notice and check results id of the next new block")
        response_notice_new_block2 = self.get_notice(subscription_callback_id, object_id="1.{}.".format(
            self.echo.config.object_types.block_result))
        check_that(
            "''results_id' of a new block'",
            response_notice_new_block2["results_id"],
            is_list(is_([])),
        )

        lcc.set_step("Check neighboring blocks")
        require_that(
            "'block and its neighboring block do not match'",
            response_notice_new_block1 != response_notice_new_block2, is_(True),
        )
        block1 = response_notice_new_block1["id"]
        block1 = int(block1.split(".")[2])
        block2 = response_notice_new_block2["id"]
        block2 = int(block2.split(".")[2])
        check_that(
            "'block_id and its neighboring block_id differ by one'",
            block2 - block1, is_(1),
        )


@lcc.prop("testing", "positive")
@lcc.tags("set_subscribe_callback")
@lcc.suite("Positive testing of method 'set_subscribe_callback'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def set_subscribe_callback(self, callback, notify_remove_create=True):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Check notices of dynamic object '2.1.0'")
    @lcc.depends_on("DatabaseApi.SetSubscribeCallback.SetSubscribeCallback.method_main_check")
    def check_global_property_object(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Get object '2.1.0'")
        param = "2.1.0"
        response_id = self.send_request(self.get_request("get_objects", [[param]]), self.__database_api_identifier)
        response = self.get_response(response_id)["result"][0]

        lcc.set_step("Subscription check for object updates '2.1.0'")
        object_keys = list(response)[:]
        self.get_notice(subscription_callback_id, object_id="1.{}.".format(self.echo.config.object_types.block_result))
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
        # todo: delete 2 get_notice. Bug: "ECHO-804"
        self.get_notice(subscription_callback_id, object_id="1.{}.".format(self.echo.config.object_types.block_result))
        response_notice = self.get_notice(subscription_callback_id, object_id=param)
        check_that_in(
            response_notice,
            "head_block_number", not_equal_to(response["head_block_number"]),
            "head_block_id", not_equal_to(response["head_block_id"]),
            "time", not_equal_to(response["time"]),
            "last_irreversible_block_num", not_equal_to(response["last_irreversible_block_num"]),
        )
        # todo: add. Bug: "ECHO-804"
        # lcc.set_step("Get object '2.1.0' again")
        # param = "2.1.0"
        # response_id = self.send_request(self.get_request("get_objects", [[param]]), self.__database_api_identifier)
        # response = self.get_response(response_id)["result"][0]
        #
        # lcc.set_step("Check that updated object does not match previous")
        # self.get_notice(subscription_callback_id, object_id="1.{}.".format(
        #     self.echo.config.object_types.block_result))
        # response_notice = self.get_notice(subscription_callback_id, object_id=param)
        # check_that_in(
        #     response_notice,
        #     "head_block_number", not_equal_to(response["head_block_number"]),
        #     "head_block_id", not_equal_to(response["head_block_id"]),
        #     "time", not_equal_to(response["time"]),
        #     "last_irreversible_block_num", not_equal_to(response["last_irreversible_block_num"]),
        # )

        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check that canceled all subscriptions")
        check_that(
            "'subscribe result'",
            response["result"],
            is_none(),
        )




