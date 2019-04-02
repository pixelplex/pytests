# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, check_that, has_entry, greater_than_or_equal_to

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

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
        self.__asset_api_identifier = self.get_identifier("asset")
        self.asset = "1.3.0"

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_asset_holders_count'")
    def method_main_check(self):
        lcc.set_step("Get holders count of ECHO asset")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [self.asset]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check response from method 'get_asset_holders_count'")
        check_that(
            "'number of asset '{}' holders'".format(self.asset),
            response["result"], greater_than_or_equal_to(0)
        )


@lcc.prop("testing", "positive")
@lcc.tags("asset_api", "get_asset_holders_count")
@lcc.suite("Positive testing of method 'get_asset_holders_count'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__asset_api_identifier = self.get_identifier("asset")
        self.echo_operations = EchoOperations()
        self.issuer = "test-echo-1"
        self.account_2 = "test-echo-2"
        self.account_3 = "test-echo-3"

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
        self.account_2 = self.get_account_id(self.account_2, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.account_3 = self.get_account_id(self.account_3, self.__database_api_identifier,
                                             self.__registration_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.tags("Bug: 'ECHO-576'")
    @lcc.test("Get asset holders count of new asset")
    @lcc.depends_on("AssetApi.GetAssetHoldersCount.GetAssetHoldersCount.method_main_check")
    def add_holders_to_new_asset(self, get_random_valid_asset_name):
        new_asset_name = get_random_valid_asset_name
        value = 100
        lcc.set_step("Create a new asset and get id new asset")
        new_asset_id = self.get_id_new_asset(new_asset_name)

        lcc.set_step("Get holders count of new asset")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [new_asset_id]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check response from method 'get_asset_holders_count'")
        check_that(
            "'number of asset '{}' holders'".format(new_asset_id),
            # todo: change to 0. Bug: "ECHO-576"
            response["result"], is_integer(-1)
        )

        lcc.set_step("Add new asset holders")
        new_holders = [self.issuer, self.account_2, self.account_3]
        for i in range(len(new_holders)):
            if not self.add_assets_to_account(value, new_asset_id, new_holders[i]):
                lcc.log_error("New asset holder '{}' not added".format(new_holders[i]))

        lcc.set_step("Check count of added holders")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [new_asset_id]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'number of asset '{}' holders'".format(new_asset_id),
            # todo: add 'is_integer(len(new_holders))'. Bug: "ECHO-576"
            response["result"], is_integer(len(new_holders) - 1)
        )


@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_asset_holders_count")
@lcc.suite("Negative testing of method 'get_asset_holders_count'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__asset_api_identifier = self.get_identifier("asset")
        self.list_asset_ids = []
        self.nonexistent_asset_id = None

    def get_nonexistent_asset_id(self, symbol=""):
        response_id = self.send_request(self.get_request("list_assets", [symbol, 100]), self.__database_api_identifier)
        response = self.get_response(response_id)
        for i in range(len(response["result"])):
            self.list_asset_ids.append(response["result"][i]["id"])
        if len(response["result"]) == 100:
            return self.get_nonexistent_asset_id(symbol=response["result"][-1]["symbol"])
        sorted_list_asset_ids = sorted(self.list_asset_ids, key=self.get_value_for_sorting_func)
        return "1.3.{}".format(str(int(sorted_list_asset_ids[-1][4:]) + 1))

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.nonexistent_asset_id = self.get_nonexistent_asset_id()

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent asset_id")
    # todo: add test. Bug: "ECHO-682"
    @lcc.tags("Bug: 'ECHO-682'")
    @lcc.disabled()
    @lcc.depends_on("AssetApi.GetAssetHoldersCount.GetAssetHoldersCount.method_main_check")
    def nonexistent_asset_id_in_method_call(self):
        lcc.set_step("Get nonexistent asset holders_count")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [self.nonexistent_asset_id]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_asset_holders_count' return error message",
            response, has_entry("error"), quiet=True,
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
            response_id = self.send_request(self.get_request("get_asset_holders_count", random_values[i]),
                                            self.__asset_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_asset_holders_count' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )
