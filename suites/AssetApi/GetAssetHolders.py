# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, this_dict, check_that_entry, is_str, require_that, is_list, \
    has_entry, is_not_none

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

SUITE = {
    "description": "Method 'get_asset_holders'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_asset_holders")
@lcc.suite("Check work of method 'get_asset_holders'", rank=1)
class GetAssetHolders(BaseTest):

    def __init__(self):
        super().__init__()
        self.__asset_api_identifier = self.get_identifier("asset")
        self.asset = "1.3.0"

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_asset_holders'")
    def method_main_check(self):
        start = 0
        limit = 10
        lcc.set_step("Get holders of ECHO asset")
        params = [self.asset, start, limit]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check response from method 'get_asset_holders'")
        result = response["result"]
        check_that(
            "'number of asset '{}' holders'".format(self.asset),
            len(result), is_(limit)
        )
        for i in range(len(result)):
            holders = result[i]
            with this_dict(holders):
                check_that_entry("name", is_str())
                check_that_entry("account_id", is_str())
                self.check_uint64_numbers(holders, "amount")


@lcc.prop("testing", "positive")
@lcc.tags("asset_api", "get_asset_holders")
@lcc.suite("Positive testing of method 'get_asset_holders'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__asset_api_identifier = self.get_identifier("asset")
        self.echo_operations = EchoOperations()
        self.asset = "1.3.0"
        self.account_1_name = "test-echo-1"
        self.account_2_name = "test-echo-2"
        self.account_3_name = "test-echo-3"
        self.account_1 = None
        self.account_2 = None
        self.account_3 = None

    def get_accounts_ids(self, account_name, account_count):
        holders_ids = []
        for i in range(account_count):
            holders_ids.append(self.get_account_id(account_name + str(i), self.__database_api_identifier,
                                                   self.__registration_api_identifier))
        return holders_ids

    def get_asset_id(self, symbol):
        params = [symbol, 1]
        response_id = self.send_request(self.get_request("list_assets", params), self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"][0]["symbol"] != symbol:
            operation = self.echo_operations.get_asset_create_operation(echo=self.echo, issuer=self.account_1,
                                                                        symbol=symbol)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)
            return self.get_operation_results_ids(broadcast_result)
        return response["result"][0]["id"]

    def add_assets_to_account(self, value, asset_id, to_account):
        operation = self.echo_operations.get_asset_issue_operation(echo=self.echo, issuer=self.account_1,
                                                                   value_amount=value, value_asset_id=asset_id,
                                                                   issue_to_account=to_account)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)
        return self.is_operation_completed(broadcast_result, expected_static_variant=0)

    def check_start_and_limit_params(self, asset_id, start, limit, account_names, accounts_ids, asset_value):
        params = [asset_id, start, limit]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id)
        result = response["result"]
        require_that(
            "'number of asset '{}' holders'".format(asset_id),
            len(result), is_(limit)
        )
        for i in range(limit):
            holders_info = result[i]
            with this_dict(holders_info):
                check_that_entry("name", is_(account_names + str(start + i)))
                check_that_entry("account_id", is_(accounts_ids[start + i]))
                check_that_entry("amount", is_(asset_value))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.account_1 = self.get_account_id(self.account_1_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.account_2 = self.get_account_id(self.account_2_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.account_3 = self.get_account_id(self.account_3_name, self.__database_api_identifier,
                                             self.__registration_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Get info about the new asset holders")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def add_holders_to_new_asset(self, get_random_valid_asset_name):
        new_asset_name = get_random_valid_asset_name
        asset_value = 100
        lcc.set_step("Create a new asset and get id new asset")
        new_asset_id = self.get_asset_id(new_asset_name)

        lcc.set_step("Add new asset holders")
        new_holders = [self.account_1, self.account_2, self.account_3]
        for i in range(len(new_holders)):
            if not self.add_assets_to_account(asset_value - i, new_asset_id, new_holders[i]):
                lcc.log_error("New asset holder '{}' not added".format(new_holders[i]))

        lcc.set_step("Check new asset holders")
        start = 0
        limit = 100
        new_holders_names = [self.account_1_name, self.account_2_name, self.account_3_name]
        params = [new_asset_id, start, limit]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id)
        result = response["result"]
        check_that(
            "'number of asset '{}' holders'".format(new_asset_id),
            len(result), is_(len(new_holders))
        )
        for i in range(len(result)):
            holders_info = result[i]
            with this_dict(holders_info):
                check_that_entry("name", is_(new_holders_names[i]))
                check_that_entry("account_id", is_(new_holders[i]))
                check_that_entry("amount", is_(asset_value - i))

    @lcc.prop("type", "method")
    @lcc.tags("Bug: 'ECHO-576'")
    @lcc.test("Check work of start and limit params")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    # todo: change to run on a empty node. Remove creation of accounts.
    def work_of_start_and_limit_params(self):
        asset_name = "LEX"
        account_names = "acc-echo-"
        asset_value = 2
        max_limit = 100
        lcc.set_step("Create asset and get id new asset")
        asset_id = self.get_asset_id(asset_name)

        lcc.set_step("Get or register accounts, the number of which is equal to the max limit 'get_asset_holders'")
        accounts_ids = self.get_accounts_ids(account_names, max_limit)
        lcc.log_info("Accounts count: {}, list:\n{}".format(len(accounts_ids), accounts_ids))

        lcc.set_step("Add holders to asset, if needed")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [asset_id]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)
        # todo: remove '+ 1'. Bug: "ECHO-576"
        if response["result"] + 1 < max_limit:
            for i in range(max_limit):
                if not self.add_assets_to_account(asset_value, asset_id, accounts_ids[i]):
                    lcc.log_error("New asset holder '{}' not added".format(accounts_ids[i]))

        lcc.set_step("Check maximum list length asset holders")
        start = 0
        limit = max_limit
        self.check_start_and_limit_params(asset_id, start, limit, account_names, accounts_ids, asset_value)

        lcc.set_step("Check minimum list length asset holders")
        start = 0
        limit = 1
        self.check_start_and_limit_params(asset_id, start, limit, account_names, accounts_ids, asset_value)

        lcc.set_step("Check start and limit param")
        start = 25
        limit = 25
        self.check_start_and_limit_params(asset_id, start, limit, account_names, accounts_ids, asset_value)


@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_asset_holders")
@lcc.suite("Negative testing of method 'get_asset_holders'", rank=3)
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

    def get_asset_id(self, symbol):
        params = [symbol, 1]
        response_id = self.send_request(self.get_request("list_assets", params), self.__database_api_identifier)
        response = self.get_response(response_id)
        if response["result"][0]["symbol"] != symbol:
            operation = self.echo_operations.get_asset_create_operation(echo=self.echo, issuer=self.account_1,
                                                                        symbol=symbol)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)
            return self.get_operation_results_ids(broadcast_result)
        return response["result"][0]["id"]

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.nonexistent_asset_id = self.get_nonexistent_asset_id()

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent asset_id")
    @lcc.tags("Improve: 'ECHO-689'")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def nonexistent_asset_id_in_method_call(self):
        start = 0
        limit = 1
        params = [self.nonexistent_asset_id, start, limit]
        lcc.set_step("Get nonexistent asset holders")
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id)
        check_that(
            "'get_asset_holders'",
            response["result"], is_list([]),
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method without params")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def call_method_without_params(self):
        lcc.set_step("Call method without params")
        response_id = self.send_request(self.get_request("get_asset_holders"), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_asset_holders' return error message",
            response, has_entry("error"),
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with wrong params of all types")
    @lcc.depends_on("AssetApi.GetAssetHolders.PositiveTesting.work_of_start_and_limit_params")
    def call_method_with_wrong_params(self, get_all_random_types):
        lcc.set_step("Call method with wrong params of all types")
        asset_name = "LEX"
        asset_id = self.get_asset_id(asset_name)
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            lcc.set_step("Wrong asset param, used '{}'".format(random_type_names[i]))
            params = [random_values[i], 0, 100]
            response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

            if isinstance(random_values[i], (int, float, bool)):
                continue

            lcc.set_step("Wrong start param, used '{}'".format(random_type_names[i]))
            params = [asset_id, random_values[i], 100]
            response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

            lcc.set_step("Wrong limit param, used '{}'".format(random_type_names[i]))
            params = [asset_id, 0, random_values[i]]
            response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

    @lcc.prop("type", "method")
    @lcc.test("Call method with nonstandard params")
    @lcc.tags("qwer")
    # @lcc.depends_on("AssetApi.GetAssetHolders.PositiveTesting.work_of_start_and_limit_params")
    def call_method_with_nonstandard_params(self, get_random_integer_up_to_hundred, get_random_float_up_to_hundred,
                                            get_random_bool):
        asset_name = "LEX"
        asset_id = self.get_asset_id(asset_name)
        negative_int = get_random_integer_up_to_hundred * (-1)
        float_number = get_random_float_up_to_hundred

        lcc.set_step("Call method with start param equal to negative integers")
        params = [asset_id, negative_int, 100]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'result'",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Call method with limit param equal to negative integers")
        params = [asset_id, 0, negative_int]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_asset_holders' return error message",
            response, has_entry("error"), quiet=True,
        )

        lcc.set_step("Call method with start and limit params equal to floats")
        params = [asset_id, float_number, float_number]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'result'",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Call method with start and limit params equal to booleans")
        params = [asset_id, get_random_bool, get_random_bool]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'result'",
            response["result"], is_not_none(), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with more then limit params")
    @lcc.tags("Bug: 'ECHO-576'")
    @lcc.depends_on("AssetApi.GetAssetHolders.PositiveTesting.work_of_start_and_limit_params")
    def call_method_with_more_then_limit_params(self):
        asset_name = "LEX"
        asset_id = self.get_asset_id(asset_name)
        limit = 100
        lcc.set_step("Check asset holders count")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [asset_id]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)
        holders_count = response["result"]
        # todo: remove '- 1'. Bug: "ECHO-576"
        if holders_count != limit - 1:
            lcc.log_error("Wrong asset_id '{}', holders count: '{}'".format(asset_id, response["result"]))
            raise Exception("Wrong asset_id")
        lcc.set_step("Call method with start param > holders count")
        # todo: remove '+ 2'. Bug: "ECHO-576"
        params = [asset_id, holders_count + 2, 1]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_asset_holders'",
            response["result"], is_list([]),
        )

        lcc.set_step("Call method with limit param > limit")
        params = [asset_id, 0, limit + 1]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_asset_holders' return error message",
            response, has_entry("error"),
        )
