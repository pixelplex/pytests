# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, is_integer, is_str, check_that, has_entry, \
    is_not_none, greater_than_or_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_all_asset_holders'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("asset_api", "get_all_asset_holders")
@lcc.suite("Check work of method 'get_all_asset_holders'", rank=1)
class GetAllAssetHolders(BaseTest):

    def __init__(self):
        super().__init__()
        self.__asset_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info("Asset API identifier is '{}'".format(self.__asset_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_all_asset_holders'")
    def method_main_check(self):
        lcc.set_step("Get all asset ids with the number of holders")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), self.__asset_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_all_asset_holders'")

        lcc.set_step("Check response from method 'get_all_asset_holders'")
        result = response["result"]
        for i in range(len(result)):
            holders = result[i]
            with this_dict(holders):
                check_that_entry("asset_id", is_str())
                check_that_entry("count", greater_than_or_equal_to(0))


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("asset_api", "get_all_asset_holders")
@lcc.suite("Positive testing of method 'get_all_asset_holders'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__asset_api_identifier = None
        self.echo_acc0 = None
        self.new_asset_name = None
        self.new_asset_id = None
        self.position_on_the_list = None

    def get_all_asset_holders(self, negative=False):
        lcc.log_info("Get all asset holders")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), self.__asset_api_identifier)
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
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("New asset in 'get_all_asset_holders' without holders")
    @lcc.depends_on("AssetApi.GetAllAssetHolders.GetAllAssetHolders.method_main_check")
    def new_asset_without_holders(self, get_random_valid_asset_name):
        self.new_asset_name = get_random_valid_asset_name
        lcc.set_step("Create a new asset and get id new asset")
        self.new_asset_id = self.utils.get_asset_id(self, self.new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(self.new_asset_id))

        lcc.set_step("Check that the new asset is in the list and its number of holders is zero")
        response = self.get_all_asset_holders()
        result = response["result"]
        for i in range(len(result)):
            assets_ids = result[i]
            if assets_ids.get("asset_id") == self.new_asset_id:
                self.position_on_the_list = i
        if self.position_on_the_list is None:
            lcc.log_error(
                "No new asset '{}' in list, id of new asset '{}'".format(self.new_asset_name, self.new_asset_id))
        with this_dict(result[self.position_on_the_list]):
            check_that_entry("asset_id", is_str(self.new_asset_id))
            check_that_entry("count", is_integer(0))

    @lcc.prop("type", "method")
    @lcc.test("New asset in 'get_all_asset_holders' with holders")
    @lcc.depends_on("AssetApi.GetAllAssetHolders.PositiveTesting.new_asset_without_holders")
    def new_asset_with_holders(self):
        value = 100
        lcc.set_step("Add new asset holder")
        self.utils.add_assets_to_account(self, value, self.new_asset_id, self.echo_acc0, self.__database_api_identifier)
        lcc.log_info(
            "Echo account '{}' became new asset holder of '{}' asset_id".format(self.echo_acc0, self.new_asset_id))

        lcc.set_step("Check that the new asset is in the list and its number of holders is zero")
        response = self.get_all_asset_holders()
        result = response["result"]
        for i in range(len(result)):
            assets_ids = result[i]
            if assets_ids.get("asset_id") == self.new_asset_id:
                self.position_on_the_list = i
        if self.position_on_the_list is None:
            lcc.log_error(
                "No new asset '{}' in list, id of new asset '{}'".format(self.new_asset_name, self.new_asset_id))
        with this_dict(result[self.position_on_the_list]):
            check_that_entry("asset_id", is_str(self.new_asset_id))
            check_that_entry("count", is_integer(1))


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("asset_api", "get_all_asset_holders")
@lcc.suite("Negative testing of method 'get_all_asset_holders'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__asset_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info("Asset API identifier is '{}'".format(self.__asset_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.depends_on("AssetApi.GetAllAssetHolders.GetAllAssetHolders.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            response_id = self.send_request(self.get_request("get_all_asset_holders", random_values[i]),
                                            self.__asset_api_identifier)
            response = self.get_response(response_id, negative=True)
            if random_type_names[i] == "random_list":
                check_that(
                    "'get_all_asset_holders' return result with '{}' params".format(random_type_names[i]),
                    response, is_not_none(), quiet=True,
                )
                continue
            check_that(
                "'get_all_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )
