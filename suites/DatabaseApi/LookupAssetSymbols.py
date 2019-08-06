# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, this_dict, check_that_entry, is_str, is_list, is_integer, \
    is_dict, equal_to, check_that, is_none, has_length

from common.base_test import BaseTest
from project import ECHO_ASSET_SYMBOL

SUITE = {
    "description": "Method 'lookup_asset_symbols'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "lookup_asset_symbols")
@lcc.suite("Check work of method 'lookup_asset_symbols'", rank=1)
class LookupAssetSymbols(BaseTest):

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

            check_that_entry("precision", is_integer(8))
            if not self.validator.is_asset_name(asset["symbol"]):
                lcc.log_error("Wrong format of 'symbol', got: {}".format(asset["symbol"]))
            else:
                lcc.log_info("'symbol' has correct format: asset_name")
            check_that_entry("extensions", is_list(), quiet=True)

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'lookup_asset_symbols'")
    def method_main_check(self):
        lcc.set_step("Lookup default asset of the chain using it symbol")
        symbols_or_ids = [self.echo_symbol]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [symbols_or_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(symbols_or_ids))

        lcc.set_step("Check simple work of method 'lookup_asset_symbols'")
        asset_by_symbol = response["result"][0]

        require_that(
            "'length of asset got by symbol'",
            asset_by_symbol, has_length(7)
        )
        self.check_asset_structure(asset_by_symbol)

        lcc.set_step("Lookup default asset of the chain using it asset_id")
        symbols_or_ids = [self.echo_asset]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [symbols_or_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            symbols_or_ids))
        asset_by_id = response["result"][0]
        require_that(
            "'length of asset got by id'",
            asset_by_symbol, has_length(7)
        )
        self.check_asset_structure(asset_by_id)
        lcc.set_step("Compare 'lookup_asset_symbols' method calls results with different type of input params")


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "lookup_asset_symbols")
@lcc.suite("Positive testing of method 'lookup_asset_symbols'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None

    @staticmethod
    def proliferate_asset_names(asset_name_base, total_asset_count):
        return ['{}{}'.format(asset_name_base, 'A' * num) for num in range(total_asset_count)]

    @staticmethod
    def compare_assets(asset_info, performed_operation, asset_is_created=False):
        if performed_operation["symbol"] == asset_info["symbol"]:
            if asset_is_created:
                performed_operation["common_options"]["core_exchange_rate"]["quote"]["asset_id"] = \
                    asset_info["options"]["core_exchange_rate"]["quote"]["asset_id"]
            with this_dict(asset_info):
                check_that_entry("issuer", equal_to(performed_operation["issuer"]))
                check_that_entry("symbol", equal_to(performed_operation["symbol"]))
                check_that_entry("precision", equal_to(performed_operation["precision"]))
                performed_options_field_name = "options"
                if asset_is_created:
                    performed_options_field_name = "common_options"
                check_that_entry("options", equal_to(performed_operation[performed_options_field_name]))

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
    @lcc.test("Create assets using asset_create operation and lookup info about them")
    @lcc.depends_on("DatabaseApi.LookupAssetSymbols.LookupAssetSymbols.method_main_check")
    def lookup_info_about_created_assets(self, get_random_valid_asset_name):
        lcc.set_step("Generate assets symbols")
        asset_name_base = get_random_valid_asset_name
        total_asset_count = 2
        generated_assets = self.proliferate_asset_names(asset_name_base, total_asset_count)
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

        lcc.set_step("Lookup created assets by symbols")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [generated_assets]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            generated_assets))

        lcc.set_step("Check created assets")
        assets_by_symbol = response["result"]
        for operation_num in range(len(collected_operations)):
            performed_operation = collected_operations[operation_num][0][1]
            for asset_by_symbol_info in assets_by_symbol:
                self.compare_assets(asset_by_symbol_info, performed_operation, asset_is_created=True)

        lcc.set_step("Lookup created assets by ids")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [asset_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            generated_assets))

        lcc.set_step("Check created assets")
        assets_by_ids = response["result"]
        for asset_by_symbol_info in assets_by_symbol:
            for asset_by_id_info in assets_by_ids:
                self.compare_assets(asset_by_id_info, asset_by_symbol_info)

        lcc.set_step("Lookup created assets by mixed input parameters (symbol and id)")
        mixed_symbols_or_ids = [asset_ids[0], generated_assets[1]]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [mixed_symbols_or_ids]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            mixed_symbols_or_ids))

        lcc.set_step("Check created assets")
        assets_by_mixed_params = response["result"]
        for asset_by_id_info in assets_by_ids:
            for asset_by_mixed_params_info in assets_by_mixed_params:
                self.compare_assets(asset_by_mixed_params_info, asset_by_id_info)

    @lcc.prop("type", "method")
    @lcc.test("Lookup nonexistent assets")
    @lcc.depends_on("DatabaseApi.LookupAssetSymbols.LookupAssetSymbols.method_main_check")
    def lookup_info_about_nonexistent_assets(self):
        lcc.set_step("Generate nonexistent asset symbol")
        nonexistent_asset_symbols = [self.utils.get_nonexistent_asset_symbol(self, self.__database_api_identifier)]
        lcc.log_info("Nonexistent asset symbol: {}".format(nonexistent_asset_symbols))

        lcc.set_step("Lookup nonexistent asset by symbol")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [nonexistent_asset_symbols]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            nonexistent_asset_symbols))

        lcc.set_step("Check nonexistent asset")
        nonexistent_asset_by_symbol = response["result"]
        for nonexistent_result in nonexistent_asset_by_symbol:
            check_that("'lookup_asset_symbols result'", nonexistent_result, is_none())

        lcc.set_step("Generate nonexistent asset_id")
        nonexistent_asset_id = [self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier)]
        lcc.log_info('Nonexistent asset id: {}'.format(nonexistent_asset_id))

        lcc.set_step("Lookup nonexistent asset by id")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [nonexistent_asset_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            nonexistent_asset_symbols))

        lcc.set_step("Check nonexistent asset")
        nonexistent_asset_by_id = response["result"]
        for nonexistent_result in nonexistent_asset_by_id:
            check_that("'get_assets result'", nonexistent_result, is_none())

    @lcc.prop("type", "method")
    @lcc.test("Compare 'lookup_asset_symbols' result with 'get_objects' result")
    @lcc.depends_on("DatabaseApi.LookupAssetSymbols.LookupAssetSymbols.method_main_check")
    def compare_with_method_get_objects(self):
        lcc.set_step("Lookup ECHO asset by id")
        response_id = self.send_request(self.get_request("lookup_asset_symbols", [[self.echo_asset]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'lookup_asset_symbols' with symbols_or_ids='{}' parameter".format(
            self.echo_asset))

        asset_object_by_lookup = response["result"][0]

        lcc.set_step("Get object of ECHO asset")
        response_id = self.send_request(self.get_request("get_objects", [[self.echo_asset]]),
                                        self.__database_api_identifier)

        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_objects' with param: {}".format(self.echo_asset))
        asset_object_by_get_object = response["result"][0]

        lcc.set_step("Compare asset objects (by 'lookup_asset_symbols' and 'get_objects' methods)")
        self.compare_assets(asset_object_by_lookup, asset_object_by_get_object)
