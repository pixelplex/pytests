# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_not_none, has_entry

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "Asset Api"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("asset_api")
@lcc.suite("Asset API")
class AssetApi(object):

    @lcc.tags("connection_to_asset_api", "connection_to_apis")
    @lcc.test("Check connection to AssetApi")
    def connection_to_asset_api(self):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting Access to a Asset API")
        api_identifier = base.get_identifier("asset")
        check_that("'asset api identifier'", api_identifier, is_integer())

        lcc.set_step("Check Asset api identifier. Call asset api method 'get_all_asset_holders'")
        response_id = base.send_request(base.get_request("get_all_asset_holders"), api_identifier)
        response = base.get_response(response_id)

        check_that(
            "'call method 'get_all_asset_holders''",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Check that Asset api identifier is unique")
        response_id = base.send_request(base.get_request("get_all_asset_holders"), api_identifier + 1)
        response = base.get_response(response_id, negative=True, log_response=True)

        check_that(
            "'using another identifier gives an error'",
            response, has_entry("error"), quiet=True
        )

        base.ws.close()
