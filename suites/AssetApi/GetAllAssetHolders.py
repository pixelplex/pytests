# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, is_integer, is_str, check_that, has_entry

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

SUITE = {
    "description": "Method 'get_all_asset_holders'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_all_asset_holders")
@lcc.suite("Check work of method 'get_all_asset_holders'", rank=1)
class GetAllAssetHolders(BaseTest):

    def __init__(self):
        super().__init__()
        self.__asset_api_identifier = self.get_identifier("asset")

    @lcc.prop("type", "method")
    @lcc.tags("Bug: 'ECHO-576'")
    @lcc.test("Simple work of method 'get_all_asset_holders'")
    def method_main_check(self):
        lcc.set_step("Get all asset ids with the number of holders")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), self.__asset_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check response from method 'get_all_asset_holders'")
        result = response["result"]
        for i in range(len(result)):
            required_fee = result[i]
            with this_dict(required_fee):
                check_that_entry("asset_id", is_str())
                # todo: add 'greater_than_or_equal_to(0)'. Bug: "ECHO-576"
                check_that_entry("count", is_integer())


@lcc.prop("testing", "positive")
@lcc.tags("asset_api", "get_all_asset_holders")
@lcc.suite("Positive testing of method 'get_all_asset_holders'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__asset_api_identifier = self.get_identifier("asset")
        self.echo_operations = EchoOperations()
        self.issuer = "test-echo-1"
        self.new_asset_name = None
        self.new_asset_id = None
        self.position_on_the_list = None

    def get_id_new_asset(self, symbol):
        operation = self.echo_operations.get_asset_create_operation(echo=self.echo, issuer=self.issuer,
                                                                    symbol=symbol)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)
        return self.get_operation_results_ids(broadcast_result)

    def add_assets_to_account(self, value, asset_id, to_account):
        operation = self.echo_operations.get_asset_issue_operation(echo=self.echo, issuer=self.issuer,
                                                                   value_amount=value, value_asset_id=asset_id,
                                                                   issue_to_account=to_account)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)
        return self.is_operation_completed(broadcast_result, expected_static_variant=0)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.issuer = self.get_account_id(self.issuer, self.__database_api_identifier,
                                          self.__registration_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.tags("Bug: 'ECHO-576'")
    @lcc.test("New asset in 'get_all_asset_holders' without holders")
    @lcc.depends_on("AssetApi.GetAllAssetHolders.GetAllAssetHolders.method_main_check")
    def new_asset_without_holders(self, get_random_valid_asset_name):
        self.new_asset_name = get_random_valid_asset_name
        lcc.set_step("Create a new asset and get id new asset")
        self.new_asset_id = self.get_id_new_asset(self.new_asset_name)

        lcc.set_step("Check that the new asset is in the list and its number of holders is zero")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), self.__asset_api_identifier)
        response = self.get_response(response_id)
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
            # todo: add 'is_integer(0)'. Bug: "ECHO-576"
            check_that_entry("count", is_integer())

    @lcc.prop("type", "method")
    @lcc.tags("Bug: 'ECHO-576'")
    @lcc.test("New asset in 'get_all_asset_holders' with holders")
    @lcc.depends_on("AssetApi.GetAllAssetHolders.PositiveTesting.new_asset_without_holders")
    def new_asset_with_holders(self):
        value = 100
        lcc.set_step("Add new asset holder")
        if not self.add_assets_to_account(value, self.new_asset_id, self.issuer):
            lcc.log_error("New asset holder '{}' not added".format(self.issuer))

        lcc.set_step("Check that the new asset is in the list and its number of holders is zero")
        response_id = self.send_request(self.get_request("get_all_asset_holders"), self.__asset_api_identifier)
        response = self.get_response(response_id)
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
            # todo: change to 'is_integer(1)'. Bug: "ECHO-576"
            check_that_entry("count", is_integer(0))


@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_all_asset_holders")
@lcc.suite("Negative testing of method 'get_all_asset_holders'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__asset_api_identifier = self.get_identifier("asset")

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.tags("Bug: 'ECHO-683'")
    @lcc.depends_on("AssetApi.GetAllAssetHolders.GetAllAssetHolders.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-683"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_all_asset_holders", random_values[i]),
                                            self.__asset_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_all_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )
