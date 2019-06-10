# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, check_that, has_entry, greater_than_or_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_asset_holders_count'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_asset_holders_count")
@lcc.suite("Check work of method 'get_asset_holders_count'", rank=1)
class GetAssetHoldersCount(BaseTest):

    def __init__(self):
        super().__init__()
        self.__asset_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info(
            "Asset API identifiers is '{}'".format(self.__asset_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_asset_holders_count'")
    def method_main_check(self):
        lcc.set_step("Get holders count of ECHO asset")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [self.echo_asset]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_asset_holders_count' of '{}' asset_id".format(self.echo_asset))

        lcc.set_step("Check response from method 'get_asset_holders_count'")
        check_that(
            "'number of asset '{}' holders'".format(self.echo_asset),
            response["result"], greater_than_or_equal_to(0)
        )


@lcc.prop("testing", "positive")
@lcc.tags("asset_api", "get_asset_holders_count")
@lcc.suite("Positive testing of method 'get_asset_holders_count'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__asset_api_identifier = None

    def get_asset_holders_count(self, asset_id, negative=False):
        lcc.log_info("Get '{}' asset holders count".format(asset_id))
        response_id = self.send_request(self.get_request("get_asset_holders_count", [asset_id]),
                                        self.__asset_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "asset='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                self.__asset_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc2 = self.get_account_id(self.echo_acc2, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc1, self.echo_acc2))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Get asset holders count of new asset")
    @lcc.depends_on("AssetApi.GetAssetHoldersCount.GetAssetHoldersCount.method_main_check")
    def add_holders_to_new_asset(self, get_random_valid_asset_name):
        new_asset_name = get_random_valid_asset_name
        value = 100
        lcc.set_step("Create a new asset and get id new asset")
        new_asset_id = self.utils.get_asset_id(self, new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset_id))

        lcc.set_step("Get holders count of new asset")
        response = self.get_asset_holders_count(new_asset_id)

        lcc.set_step("Check response from method 'get_asset_holders_count'")
        check_that(
            "'number of asset '{}' holders'".format(new_asset_id),
            response["result"], is_integer(0)
        )

        lcc.set_step("Add new asset holders")
        new_holders = [self.echo_acc0, self.echo_acc1, self.echo_acc2]
        for i in range(len(new_holders)):
            self.utils.add_assets_to_account(self, value, new_asset_id, new_holders[i], self.__database_api_identifier)
        lcc.log_info(
            "Echo accounts '{}' became new asset holders of '{}' asset_id".format(new_holders, new_asset_id))

        lcc.set_step("Check count of added holders")
        response = self.get_asset_holders_count(new_asset_id)
        check_that(
            "'number of asset '{}' holders'".format(new_asset_id),
            response["result"], is_integer(len(new_holders))
        )


@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_asset_holders_count")
@lcc.suite("Negative testing of method 'get_asset_holders_count'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__asset_api_identifier = None
        self.nonexistent_asset_id = None

    def get_asset_holders_count(self, asset_id, negative=False):
        response_id = self.send_request(self.get_request("get_asset_holders_count", [asset_id]),
                                        self.__asset_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info(
            "API identifiers are: database='{}', asset='{}'".format(self.__database_api_identifier,
                                                                    self.__asset_api_identifier))
        self.nonexistent_asset_id = self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier)
        lcc.log_info("Nonexistent asset id is '{}'".format(self.nonexistent_asset_id))

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent asset_id")
    @lcc.depends_on("AssetApi.GetAssetHoldersCount.GetAssetHoldersCount.method_main_check")
    def nonexistent_asset_id_in_method_call(self):
        lcc.set_step("Get nonexistent asset holders_count")
        response = self.get_asset_holders_count(self.nonexistent_asset_id)
        check_that(
            "'get_asset_holders_count' return error message",
            response["result"], is_integer(0),
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method without params")
    @lcc.depends_on("AssetApi.GetAssetHoldersCount.GetAssetHoldersCount.method_main_check")
    def call_method_without_params(self):
        lcc.set_step("Call method without params")
        response_id = self.send_request(self.get_request("get_asset_holders_count"), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_asset_holders_count' return error message",
            response, has_entry("error"), quiet=True,
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with wrong params of all types")
    @lcc.depends_on("AssetApi.GetAssetHoldersCount.GetAssetHoldersCount.method_main_check")
    def call_method_wrong_with_params(self, get_all_random_types):
        lcc.set_step("Call method with wrong params of all types")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            response = self.get_asset_holders_count(random_values[i], negative=True)
            check_that(
                "'get_asset_holders_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )
