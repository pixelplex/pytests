# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_not_none, has_entry

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "History Api"
}


@lcc.prop("testing", "main")
@lcc.tags("history_api")
@lcc.suite("History API")
class HistoryApi(object):

    @lcc.tags("connection_to_history_api")
    @lcc.test("Check connection to HistoryApi")
    def connection_to_history_api(self):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a History API")
        api_identifier = base.get_identifier("history")
        check_that("'history api identifier'", api_identifier, is_integer())

        lcc.set_step("Check History api identifier. Call history api method 'get_account_history'")
        params = ["1.2.0", "1.10.0", 3, "1.10.0"]
        response_id = base.send_request(base.get_request("get_account_history", params), api_identifier)
        response = base.get_response(response_id, log_response=True)

        check_that(
            "'call method 'get_account_history''",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Check that History api identifier is unique")
        response_id = base.send_request(base.get_request("get_account_history", params), api_identifier + 1)
        response = base.get_response(response_id, negative=True, log_response=True)

        check_that(
            "'using another identifier gives an error'",
            response, has_entry("error"), quiet=True
        )

        base.ws.close()
