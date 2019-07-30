# -*- coding: utf-8 -*-
import re

import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, this_dict, check_that_entry, is_str, is_list, is_integer, \
    is_dict, equal_to, check_that, has_length, match_pattern

from common.base_test import BaseTest
from project import ECHO_ASSET_SYMBOL

SUITE = {
    "description": "Method 'list_assets'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "list_assets")
@lcc.suite("Check work of method 'list_assets'", rank=1)
class ListAssets(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.echo_symbol = ECHO_ASSET_SYMBOL

    def check_core_exchange_rate_structure(self, core_exchange_rate):
        with this_dict(core_exchange_rate):
            check_that_entry("base", is_dict(), quiet=True)
            check_that_entry("quote", is_dict(), quiet=True)
            for key in core_exchange_rate:
                core_exchange_rate_part = core_exchange_rate[key]
                with this_dict(core_exchange_rate_part):
                    self.check_uint64_numbers(core_exchange_rate_part, "amount", quiet=True)
                    if not self.validator.is_asset_id(core_exchange_rate_part["asset_id"]):
                        lcc.log_error("Wrong format of {} 'asset_id', got: {}".format(
                            key, core_exchange_rate_part["asset_id"]))
                    else:
                        lcc.log_info("{} 'asset_id' has correct format: asset_id".format(key))

    def check_asset_structure(self, asset):
        with this_dict(asset):
            if not self.validator.is_asset_id(asset["id"]):
                lcc.log_error("Wrong format of 'id', got: {}".format(asset["id"]))
            else:
                lcc.log_info("'id' has correct format: asset_id")
            if not self.validator.is_dynamic_asset_data_id(asset["dynamic_asset_data_id"]):
                lcc.log_error("Wrong format of 'dynamic_asset_data_id', got: {}".format(
                    asset["dynamic_asset_data_id"]))
            else:
                lcc.log_info("'dynamic_asset_data_id' has correct format: dynamic_asset_data_id")

            if not self.validator.is_account_id(asset["issuer"]):
                lcc.log_error("Wrong format of 'issuer', got: {}".format(asset["issuer"]))
            else:
                lcc.log_info("'issuer' has correct format: account_id")

            check_that_entry("options", is_dict(), quiet=True)
            options = asset["options"]
            with this_dict(options):
                require_that("'options'", options, has_length(12))
                check_that_entry("blacklist_authorities", is_list(), quiet=True)
                check_that_entry("blacklist_markets", is_list(), quiet=True)
                check_that_entry("core_exchange_rate", is_dict(), quiet=True)

                core_exchange_rate = options["core_exchange_rate"]
                require_that(
                    "'core_exchange_rate'",
                    core_exchange_rate, has_length(2)
                )
                self.check_core_exchange_rate_structure(core_exchange_rate)

                check_that_entry("description", is_str(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)
                check_that_entry("flags", is_integer(), quiet=True)
                check_that_entry("issuer_permissions", is_integer(), quiet=True)
                check_that_entry("market_fee_percent", is_integer(), quiet=True)

                self.check_uint64_numbers(options, "max_market_fee", quiet=True)
                self.check_uint64_numbers(options, "max_supply", quiet=True)
                check_that_entry("whitelist_authorities", is_list(), quiet=True)
                check_that_entry("whitelist_markets", is_list(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)

            check_that_entry("precision", is_integer(8))
            if not self.validator.is_asset_name(asset["symbol"]):
                lcc.log_error("Wrong format of 'symbol', got: {}".format(asset["symbol"]))
            else:
                lcc.log_info("'symbol' has correct format: asset_name")

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'list_assets'")
    def method_main_check(self):
        lcc.set_step("List default asset of the chain")
        limit = 1
        response_id = self.send_request(self.get_request("list_assets", [self.echo_symbol, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'list_assets' with lower_bound_symbol='{}', limit={} parameters".format(
            self.echo_symbol, limit))
        asset = response["result"][0]

        require_that(
            "'length of default chain asset'",
            asset, has_length(7)
        )
        self.check_asset_structure(asset)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "list_assets")
@lcc.suite("Positive testing of method 'list_assets'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def proliferate_asset_names(asset_name_base, total_asset_count):
        return ['{}{}'.format(asset_name_base, 'A' * num) for num in range(total_asset_count)], asset_name_base

    def get_assets_limit_more_than_exists(self, return_symbol=False):
        if return_symbol:
            _id, symbol = self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier,
                                                              return_symbol=return_symbol)
            return int(_id[_id.rfind('.') + 1:]) + 1, symbol
        _id = self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier,
                                                  return_symbol=return_symbol)
        return int(_id[_id.rfind('.') + 1:]) + 1

    @staticmethod
    def check_limit_value_range(limit):
        if limit > 100:
            limit = (limit % 100) + 1
            return limit, True
        return limit, False

    @staticmethod
    def check_created_asset(asset_info, performed_operation):
        if performed_operation["symbol"] == asset_info["symbol"]:
            performed_operation["common_options"]["core_exchange_rate"]["quote"]["asset_id"] = \
                asset_info["options"]["core_exchange_rate"]["quote"]["asset_id"]
            with this_dict(asset_info):
                check_that_entry("issuer", equal_to(performed_operation["issuer"]))
                check_that_entry("symbol", equal_to(performed_operation["symbol"]))
                check_that_entry("precision", equal_to(performed_operation["precision"]))
                check_that_entry("options", equal_to(performed_operation["common_options"]))

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Create assets using asset_create operation and list info about them")
    @lcc.depends_on("DatabaseApi.ListAssets.ListAssets.method_main_check")
    def list_info_about_create_assets(self, get_random_valid_asset_name):
        lcc.set_step("Generate assets symbols")
        asset_name_base = get_random_valid_asset_name
        total_asset_count = limit = 2
        generated_assets, lower_bound_symbol = self.proliferate_asset_names(asset_name_base, total_asset_count)
        lcc.log_info('Generated asset names: {}'.format(generated_assets))

        lcc.set_step("Perform assets creation operation")
        asset_ids = []
        collected_operations = []
        for asset_symbol in generated_assets:
            asset_id, collected_operation = self.utils.get_asset_id(self, asset_symbol,
                                                                    self.__database_api_identifier,
                                                                    need_operation=True)
            asset_ids.append(asset_id)
            collected_operations.append(collected_operation)
        lcc.log_info("Assets was created, ids='{}'".format(asset_ids))

        lcc.set_step("List assets")
        response_id = self.send_request(self.get_request("list_assets", [lower_bound_symbol, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'list_assets' with params: lower_bound_symbol='{}', limit={}".format(
            lower_bound_symbol, limit))

        lcc.set_step("Check created assets")
        assets_info = response["result"]
        for operation_num in range(len(collected_operations)):
            performed_operation = collected_operations[operation_num][0][1]
            for asset_info in assets_info:
                self.check_created_asset(asset_info, performed_operation)

    @lcc.prop("type", "method")
    @lcc.test("List assets with set `limit` parameter more than exist in chain")
    @lcc.depends_on("DatabaseApi.ListAssets.ListAssets.method_main_check")
    def list_more_assets_than_exists(self):
        lcc.set_step("Get assets limit, more than exists")
        limit, lower_bound_symbol = self.get_assets_limit_more_than_exists(return_symbol=True)
        lcc.log_info("Total assets count in chain: {}".format(limit))

        limit, limit_change_status = self.check_limit_value_range(limit)
        if limit_change_status:
            lcc.log_info("'Limit' value change to {}, reason - {} is a maximum available value".format(
                limit, 100))
        lcc.log_info("Got 'limit' value={}, 'lower_bound_symbol' value = '{}'".format(limit,
                                                                                      lower_bound_symbol))

        lcc.set_step("List assets")
        response_id = self.send_request(self.get_request("list_assets", [lower_bound_symbol,
                                                                         limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'list_assets' with params: lower_bound_symbol='{}', limit={}".format(
            lower_bound_symbol, limit))

        lcc.set_step("Check listed assets")
        assets = response["result"]
        require_that(
            "'length of listed assets'",
            assets, has_length(limit - 1)
        )

    @lcc.prop("type", "method")
    @lcc.test("Check alphabet order in full listed assets")
    @lcc.depends_on("DatabaseApi.ListAssets.ListAssets.method_main_check")
    def check_alphabet_order_in_full_listed_assets(self):
        limit, lower_bound_symbol = 100, ""

        lcc.set_step("List assets")
        response_id = self.send_request(self.get_request("list_assets", [lower_bound_symbol, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'list_assets' with params: lower_bound_symbol='{}', limit={}".format(
            lower_bound_symbol, limit))

        assets = response["result"]

        lcc.set_step("Make listed assets symbols list")
        listed_asset_symbols = [asset["symbol"] for asset in assets]
        lcc.log_info("Symbols list: {}".format(listed_asset_symbols))

        lcc.set_step("Make sorted listed assets symbols list")
        sorted_listed_asset_symbols = [asset["symbol"] for asset in assets]
        lcc.log_info("Sorted symbols list: {}".format(sorted_listed_asset_symbols))

        lcc.set_step("Check alphabet order by Symbol")
        require_that(
            "'alphabet symbol order in listed assets'",
            listed_asset_symbols, equal_to(sorted(listed_asset_symbols.copy()))
        )

    @lcc.prop("type", "method")
    @lcc.test("Check alphabet symbol order in cut listed assets and cutting rules")
    @lcc.depends_on("DatabaseApi.ListAssets.ListAssets.method_main_check")
    def check_alphabet_order_in_cut_listed_assets(self, get_random_valid_asset_name):
        lcc.set_step("Generate asset symbol")
        asset_symbol = get_random_valid_asset_name
        lower_bound_symbol = asset_symbol[:2]
        limit = 100
        lcc.log_info('Generated asset name: {}'.format(asset_symbol))

        lcc.set_step("Perform asset creation operation")
        created_asset_id = self.utils.get_asset_id(self, asset_symbol,
                                                   self.__database_api_identifier)
        lcc.log_info("Asset was created, symbol='{}' id='{}'".format(asset_symbol, created_asset_id))

        lcc.set_step("List assets")
        response_id = self.send_request(self.get_request("list_assets", [lower_bound_symbol, limit]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'list_assets' with params: lower_bound_symbol='{}', limit={}".format(
            lower_bound_symbol, limit))

        assets = response["result"]

        lcc.set_step("Make listed assets symbols list")
        listed_asset_symbols = [asset["symbol"] for asset in assets]
        lcc.log_info("Symbols list: {}".format(listed_asset_symbols))

        lcc.set_step("Make sorted listed assets symbols list")
        sorted_listed_asset_symbols = [asset["symbol"] for asset in assets]
        lcc.log_info("Sorted symbols list: {}".format(sorted_listed_asset_symbols))

        lcc.set_step("Check alphabet symbol order")
        check_that(
            "'symbol order in listed assets'",
            listed_asset_symbols, equal_to(sorted(listed_asset_symbols.copy()))
        )

        lcc.set_step("Check cutting rules of symbols")
        pattern_regex = "^[{}-Z][A-Z]*$".format(lower_bound_symbol[0])
        pattern = re.compile(pattern_regex)
        for asset in assets:
            check_that_entry("symbol", match_pattern(pattern), in_=asset)
