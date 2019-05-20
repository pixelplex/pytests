# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_, this_dict, check_that_entry, is_str, require_that, is_list, \
    has_entry, is_not_none

from common.base_test import BaseTest
from project import DEFAULT_ACCOUNT_PREFIX

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
        self.__asset_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__asset_api_identifier = self.get_identifier("asset")
        lcc.log_info("Asset API identifier is '{}'".format(self.__asset_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_asset_holders'")
    def method_main_check(self):
        start = 0
        limit = 7
        lcc.set_step("Get holders of ECHO asset")
        params = [self.echo_asset, start, limit]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info(
            "Call method 'get_asset_holders' with: asset='{}', start='{}', limit='{}' parameters".format(
                self.echo_asset, start, limit))

        lcc.set_step("Check response from method 'get_asset_holders'")
        result = response["result"]
        check_that(
            "'number of asset '{}' holders'".format(self.echo_asset),
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
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__asset_api_identifier = None
        self.echo_acc0_name = self.echo_acc0
        self.echo_acc1_name = self.echo_acc1
        self.echo_acc2_name = self.echo_acc2

    def get_asset_holders(self, asset_id, start, limit, negative=False):
        lcc.log_info("Get '{}' asset holders".format(asset_id))
        params = [asset_id, start, limit]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        return self.get_response(response_id, negative=negative)

    def check_start_and_limit_params(self, asset_id, start, limit, account_names, accounts_ids, asset_value):
        response = self.get_asset_holders(asset_id, start, limit)
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
                check_that_entry("amount", is_(asset_value - i))

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
    @lcc.test("Get info about the new asset holders")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def add_holders_to_new_asset(self, get_random_valid_asset_name):
        new_asset_name = get_random_valid_asset_name
        asset_value = 100
        lcc.set_step("Create a new asset and get id new asset")
        new_asset_id = self.utils.get_asset_id(self, self.echo, new_asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(new_asset_id))

        lcc.set_step("Add new asset holders")
        new_holders = [self.echo_acc0, self.echo_acc1, self.echo_acc2]
        for i in range(len(new_holders)):
            self.utils.add_assets_to_account(self, self.echo, asset_value - i, new_asset_id, new_holders[i],
                                             self.__database_api_identifier)
        lcc.log_info(
            "Echo accounts '{}' became new asset holders of '{}' asset_id".format(new_holders, new_asset_id))

        lcc.set_step("Check new asset holders")
        start = 0
        limit = 100
        new_holders_names = [self.echo_acc0_name, self.echo_acc1_name, self.echo_acc2_name]
        response = self.get_asset_holders(new_asset_id, start, limit)
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
    @lcc.test("Check work of start and limit params")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def work_of_start_and_limit_params(self, get_random_valid_asset_name):
        asset_name = get_random_valid_asset_name
        account_names = DEFAULT_ACCOUNT_PREFIX
        asset_value = max_limit = 100
        lcc.set_step("Create asset and get id new asset")
        asset_id = self.utils.get_asset_id(self, self.echo, asset_name, self.__database_api_identifier)
        lcc.log_info("New asset created, asset_id is '{}'".format(asset_id))

        lcc.set_step("Get accounts, the number of which is equal to the max limit 'get_asset_holders'")
        accounts_ids = self.get_accounts_ids(account_names, max_limit, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Accounts count: {}, list:\n{}".format(len(accounts_ids), accounts_ids))

        lcc.set_step("Add holders to asset")
        list_operations = []
        for i in range(max_limit):
            operation = self.echo_ops.get_asset_issue_operation(echo=self.echo, issuer=self.echo_acc0,
                                                                value_amount=asset_value - i, value_asset_id=asset_id,
                                                                issue_to_account=accounts_ids[i])
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            lcc.log_warn(str(collected_operation))
            list_operations.append(collected_operation)
            lcc.log_warn(str(list_operations))
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations)
        if not self.is_operation_completed(broadcast_result, expected_static_variant=0):
            raise Exception("New asset holders did not added to '{}' asset_id".format(asset_id))
        lcc.log_info(
            "Echo accounts '{}' became new asset holders of '{}' asset_id".format(accounts_ids, asset_id))

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
        self.check_start_and_limit_params(asset_id, start, limit, account_names, accounts_ids, asset_value - start)


@lcc.prop("testing", "negative")
@lcc.tags("asset_api", "get_asset_holders")
@lcc.suite("Negative testing of method 'get_asset_holders'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__asset_api_identifier = None
        self.nonexistent_asset_id = None

    def get_asset_holders(self, asset_id, start, limit, negative=False):
        params = [asset_id, start, limit]
        response_id = self.send_request(self.get_request("get_asset_holders", params), self.__asset_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__asset_api_identifier = self.get_identifier("asset")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("API identifiers are: database='{}', registration='{}', "
                     "asset='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                         self.__asset_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.nonexistent_asset_id = self.utils.get_nonexistent_asset_id(self, self.echo, self.__database_api_identifier)
        lcc.log_info("Nonexistent asset id is '{}'".format(self.nonexistent_asset_id))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent asset_id")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def nonexistent_asset_id_in_method_call(self):
        start = 0
        limit = 1
        lcc.set_step("Get nonexistent asset holders")
        response = self.get_asset_holders(self.nonexistent_asset_id, start, limit, negative=True)
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
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def call_method_with_wrong_params(self, get_all_random_types):
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())

        for i in range(len(get_all_random_types)):
            lcc.set_step("Wrong asset param, used '{}'".format(random_type_names[i]))
            response = self.get_asset_holders(random_values[i], 0, 100, negative=True)
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

            if isinstance(random_values[i], (int, float, bool)):
                continue

            lcc.set_step("Wrong start param, used '{}'".format(random_type_names[i]))
            response = self.get_asset_holders(self.echo_asset, random_values[i], 100, negative=True)
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

            lcc.set_step("Wrong limit param, used '{}'".format(random_type_names[i]))
            response = self.get_asset_holders(self.echo_asset, 0, random_values[i], negative=True)
            check_that(
                "'get_asset_holders' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

    @lcc.prop("type", "method")
    @lcc.test("Call method with nonstandard params")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def call_method_with_nonstandard_params(self, get_random_integer_up_to_hundred, get_random_float_up_to_hundred,
                                            get_random_bool):
        negative_int = get_random_integer_up_to_hundred * (-1)
        float_number = get_random_float_up_to_hundred

        lcc.set_step("Call method with start param equal to negative integers")
        response = self.get_asset_holders(self.echo_asset, negative_int, 100, negative=True)
        check_that(
            "'result'",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Call method with limit param equal to negative integers")
        response = self.get_asset_holders(self.echo_asset, 0, negative_int, negative=True)
        check_that(
            "'get_asset_holders' return error message",
            response, has_entry("error"), quiet=True,
        )

        lcc.set_step("Call method with start and limit params equal to floats")
        response = self.get_asset_holders(self.echo_asset, float_number, float_number, negative=True)
        check_that(
            "'result'",
            response["result"], is_not_none(), quiet=True
        )

        lcc.set_step("Call method with start and limit params equal to booleans")
        response = self.get_asset_holders(self.echo_asset, get_random_bool, get_random_bool, negative=True)
        check_that(
            "'result'",
            response["result"], is_not_none(), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with more then limit params")
    @lcc.depends_on("AssetApi.GetAssetHolders.GetAssetHolders.method_main_check")
    def call_method_with_more_then_limit_params(self):
        limit = 100

        lcc.set_step("Check that the asset holders are above the limit.")
        response_id = self.send_request(self.get_request("get_asset_holders_count", [self.echo_asset]),
                                        self.__asset_api_identifier)
        response = self.get_response(response_id)
        holders_count = response["result"]
        if holders_count < limit:
            lcc.log_error("Wrong asset_id '{}', holders count: '{}'".format(self.echo_asset, response["result"]))
            raise Exception("Wrong asset_id")
        lcc.log_info("Asset holders greater than or equal to limit, got: '{}'".format(holders_count))

        lcc.set_step("Call method with start param = holders count")
        response = self.get_asset_holders(self.echo_asset, holders_count, 1, negative=True)
        check_that(
            "'get_asset_holders'",
            response["result"], is_list([]),
        )

        lcc.set_step("Call method with start param > holders count")
        response = self.get_asset_holders(self.echo_asset, holders_count + 1, 1, negative=True)
        check_that(
            "'get_asset_holders'",
            response["result"], is_list([]),
        )

        lcc.set_step("Call method with limit param > limit")
        response = self.get_asset_holders(self.echo_asset, 0, limit + 1, negative=True)
        check_that(
            "'get_asset_holders' return error message",
            response, has_entry("error"),
        )
