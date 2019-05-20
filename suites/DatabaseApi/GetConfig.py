# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, has_entry, is_str

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_config'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_config")
@lcc.suite("Check work of method 'get_config'", rank=1)
class GetConfig(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_config'")
    def method_main_check(self):
        lcc.set_step("Get config")
        response_id = self.send_request(self.get_request("get_config"), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_config'")

        lcc.set_step("Check main fields")
        echo_configs = ["ECHO_MIN_ACCOUNT_NAME_LENGTH", "ECHO_MAX_ACCOUNT_NAME_LENGTH", "ECHO_MIN_ASSET_SYMBOL_LENGTH",
                        "ECHO_MAX_ASSET_SYMBOL_LENGTH", "ECHO_MAX_SHARE_SUPPLY", "ECHO_MAX_PAY_RATE",
                        "ECHO_MAX_SIG_CHECK_DEPTH", "ECHO_MIN_TRANSACTION_SIZE_LIMIT", "ECHO_MIN_BLOCK_INTERVAL",
                        "ECHO_MAX_BLOCK_INTERVAL", "ECHO_DEFAULT_BLOCK_INTERVAL", "ECHO_DEFAULT_MAX_TRANSACTION_SIZE",
                        "ECHO_DEFAULT_MAX_BLOCK_SIZE", "ECHO_DEFAULT_MAX_TIME_UNTIL_EXPIRATION",
                        "ECHO_DEFAULT_MAINTENANCE_INTERVAL", "ECHO_DEFAULT_MAINTENANCE_SKIP_SLOTS",
                        "ECHO_MIN_UNDO_HISTORY", "ECHO_MAX_UNDO_HISTORY", "ECHO_MIN_BLOCK_SIZE_LIMIT",
                        "ECHO_MIN_TRANSACTION_EXPIRATION_LIMIT", "ECHO_BLOCKCHAIN_PRECISION",
                        "ECHO_BLOCKCHAIN_PRECISION_DIGITS", "ECHO_DEFAULT_TRANSFER_FEE", "ECHO_MAX_INSTANCE_ID",
                        "ECHO_100_PERCENT", "ECHO_1_PERCENT", "ECHO_MAX_MARKET_FEE_PERCENT",
                        "ECHO_DEFAULT_FORCE_SETTLEMENT_DELAY", "ECHO_DEFAULT_FORCE_SETTLEMENT_OFFSET",
                        "ECHO_DEFAULT_FORCE_SETTLEMENT_MAX_VOLUME", "ECHO_DEFAULT_PRICE_FEED_LIFETIME",
                        "ECHO_MAX_FEED_PRODUCERS", "ECHO_DEFAULT_MAX_AUTHORITY_MEMBERSHIP",
                        "ECHO_DEFAULT_MAX_ASSET_WHITELIST_AUTHORITIES", "ECHO_DEFAULT_MAX_ASSET_FEED_PUBLISHERS",
                        "ECHO_COLLATERAL_RATIO_DENOM", "ECHO_MIN_COLLATERAL_RATIO", "ECHO_MAX_COLLATERAL_RATIO",
                        "ECHO_DEFAULT_MAINTENANCE_COLLATERAL_RATIO", "ECHO_DEFAULT_MAX_SHORT_SQUEEZE_RATIO",
                        "ECHO_DEFAULT_MARGIN_PERIOD_SEC", "ECHO_DEFAULT_MAX_COMMITTEE",
                        "ECHO_DEFAULT_MAX_PROPOSAL_LIFETIME_SEC", "ECHO_DEFAULT_COMMITTEE_PROPOSAL_REVIEW_PERIOD_SEC",
                        "ECHO_DEFAULT_NETWORK_PERCENT_OF_FEE", "ECHO_DEFAULT_LIFETIME_REFERRER_PERCENT_OF_FEE",
                        "ECHO_DEFAULT_MAX_BULK_DISCOUNT_PERCENT", "ECHO_DEFAULT_BULK_DISCOUNT_THRESHOLD_MIN",
                        "ECHO_DEFAULT_BULK_DISCOUNT_THRESHOLD_MAX", "ECHO_DEFAULT_CASHBACK_VESTING_PERIOD_SEC",
                        "ECHO_DEFAULT_CASHBACK_VESTING_THRESHOLD", "ECHO_DEFAULT_BURN_PERCENT_OF_FEE",
                        "ECHO_DEFAULT_MAX_ASSERT_OPCODE", "ECHO_DEFAULT_FEE_LIQUIDATION_THRESHOLD",
                        "ECHO_DEFAULT_ACCOUNTS_PER_FEE_SCALE", "ECHO_DEFAULT_ACCOUNT_FEE_SCALE_BITSHIFTS",
                        "ECHO_MAX_URL_LENGTH", "ECHO_NEAR_SCHEDULE_CTR_IV", "ECHO_FAR_SCHEDULE_CTR_IV",
                        "ECHO_CORE_ASSET_CYCLE_RATE", "ECHO_CORE_ASSET_CYCLE_RATE_BITS",
                        "ECHO_DEFAULT_COMMITEE_PAY_VESTING_SECONDS", "ECHO_MAX_INTEREST_APR"]
        with this_dict(response["result"]):
            if check_that("config", response["result"], has_length(70)):
                check_that_entry("ECHO_SYMBOL", is_str("ECHO"), quiet=True)
                check_that_entry("ECHO_ADDRESS_PREFIX", is_str("ECHO"), quiet=True)
                check_that_entry("ECHO_ED_PREFIX", is_str("DET"), quiet=True)
                for i in range(len(echo_configs)):
                    self.check_uint64_numbers(response["result"], echo_configs[i], quiet=True)

                if not self.validator.is_account_id(response["result"]["ECHO_COMMITTEE_ACCOUNT"]):
                    lcc.log_error("Wrong format of 'ECHO_COMMITTEE_ACCOUNT', got: {}".format(
                        response["result"]["ECHO_COMMITTEE_ACCOUNT"]))
                else:
                    lcc.log_info("'ECHO_COMMITTEE_ACCOUNT' has correct format: account_id")

                if not self.validator.is_account_id(response["result"]["ECHO_RELAXED_COMMITTEE_ACCOUNT"]):
                    lcc.log_error("Wrong format of 'ECHO_RELAXED_COMMITTEE_ACCOUNT', got: {}".format(
                        response["result"]["ECHO_RELAXED_COMMITTEE_ACCOUNT"]))
                else:
                    lcc.log_info("'ECHO_RELAXED_COMMITTEE_ACCOUNT' has correct format: account_id")

                if not self.validator.is_account_id(response["result"]["ECHO_NULL_ACCOUNT"]):
                    lcc.log_error("Wrong format of 'ECHO_NULL_ACCOUNT', got: {}".format(
                        response["result"]["ECHO_NULL_ACCOUNT"]))
                else:
                    lcc.log_info("'ECHO_NULL_ACCOUNT' has correct format: account_id")

                if not self.validator.is_account_id(response["result"]["ECHO_TEMP_ACCOUNT"]):
                    lcc.log_error("Wrong format of 'ECHO_TEMP_ACCOUNT', got: {}".format(
                        response["result"]["ECHO_TEMP_ACCOUNT"]))
                else:
                    lcc.log_info("'ECHO_TEMP_ACCOUNT' has correct format: account_id")


@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_config")
@lcc.suite("Negative testing of method 'get_config'", rank=2)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Call method with params of all types")
    @lcc.tags("Bug: 'ECHO-680'")
    @lcc.depends_on("DatabaseApi.GetConfig.GetConfig.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_config", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_config' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
