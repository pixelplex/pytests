# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, not_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'set_block_applied_callback'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "set_block_applied_callback")
@lcc.suite("Check work of method 'set_block_applied_callback'", rank=1)
class SetBlockAppliedCallback(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'set_block_applied_callback'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set block applied callback")
        subscription_callback_id = get_random_integer
        param = [subscription_callback_id]
        response_id = self.send_request(self.get_request("set_block_applied_callback", param),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check simple work of method 'set_block_applied_callback'")
        check_that(
            "'block applied callback'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Check new block hash number")
        notice = self.get_notice(subscription_callback_id, log_response=True)
        notice2 = self.get_notice(subscription_callback_id, log_response=True)
        check_that(
            "'block hash and its neighboring block hash do not match'",
            notice,
            not_equal_to(notice2),
        )
