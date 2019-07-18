# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, check_that_entry, this_dict, check_that, is_list, \
    require_that, is_, has_length, is_bool, is_dict, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_global_properties'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_global_properties")
@lcc.suite("Check work of method 'get_global_properties'", rank=1)
class GetGlobalProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None
        self.all_operations = self.echo.config.operation_ids.__dict__
        self.no_fee_count = 0
        self.only_fee_count = 0
        self.fee_with_price_per_kbyte_count = 0
        self.account_create_fee_count = 0
        self.account_update_fee_count = 0
        self.asset_create_count = 0
        self.pool_fee_count = 0

    @staticmethod
    def no_fee(actual_fee):
        check_that("fee", actual_fee, has_length(0))

    @staticmethod
    def only_fee(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(1)):
                check_that_entry("fee", is_integer(), quiet=True)

    @staticmethod
    def fee_with_price_per_kbyte(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(2)):
                check_that_entry("fee", is_integer(), quiet=True)
                check_that_entry("price_per_kbyte", is_integer(), quiet=True)

    @staticmethod
    def account_create_fee(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(3)):
                check_that_entry("basic_fee", is_integer(), quiet=True)
                check_that_entry("premium_fee", is_integer(), quiet=True)
                check_that_entry("price_per_kbyte", is_integer(), quiet=True)

    @staticmethod
    def account_update_fee(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(2)):
                check_that_entry("membership_annual_fee", is_integer(), quiet=True)
                check_that_entry("membership_lifetime_fee", is_integer(), quiet=True)

    @staticmethod
    def asset_create_fee(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(4)):
                check_that_entry("symbol3", is_integer(), quiet=True)
                check_that_entry("symbol4", is_integer(), quiet=True)
                check_that_entry("long_symbol", is_integer(), quiet=True)
                check_that_entry("price_per_kbyte", is_integer(), quiet=True)

    @staticmethod
    def pool_fee(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(2)):
                check_that_entry("fee", is_integer(), quiet=True)
                check_that_entry("pool_fee", is_integer(), quiet=True)

    def check_default_fee_for_operation(self, current_fees, operations, check_kind):
        for i in range(len(operations)):
            for j in range(len(current_fees)):
                if current_fees[j][0] == self.all_operations.get(operations[i].upper()):
                    lcc.log_info("Check default fee for '{}' operation, "
                                 "operation_id is '{}'".format(operations[i], current_fees[j][0]))
                    check_kind(current_fees[j][1])
                    break

    def check_sidechain_config(self, sidechain_config, eth_params, eth_methods):
        with this_dict(sidechain_config):
            if check_that("sidechain_config", sidechain_config, has_length(15)):
                for i in range(len(eth_params)):
                    if not self.validator.is_hex(sidechain_config[eth_params[i]]):
                        lcc.log_error(
                            "Wrong format of '{}', got: {}".format(eth_params[i], sidechain_config[eth_params[i]]))
                    else:
                        lcc.log_info("'{}' has correct format: hex".format(eth_params[i]))
                for i in range(len(eth_methods)):
                    if check_that_entry([eth_methods[i]], has_length(2)):
                        with this_dict(sidechain_config[eth_methods[i]]):
                            if not self.validator.is_hex(sidechain_config[eth_methods[i]]["method"]):
                                lcc.log_error(
                                    "Wrong format of '{}', got: {}".format(eth_methods[i],
                                                                           sidechain_config[eth_methods[i]]))
                            else:
                                lcc.log_info("'{}' has correct format: hex".format(eth_methods[i]))
                            check_that_entry("gas", is_integer(), quiet=True)
                if not self.validator.is_eth_asset_id(sidechain_config["ETH_asset_id"]):
                    lcc.log_error("Wrong format of 'ETH_asset_id', got: {}".format(sidechain_config["ETH_asset_id"]))
                else:
                    lcc.log_info("'ETH_asset_id' has correct format: eth_asset_id")
                if not self.validator.is_hex(sidechain_config["erc20_deposit_topic"]):
                    lcc.log_error("Wrong format of 'erc20_deposit_topic', got: {}".format(
                        sidechain_config["erc20_deposit_topic"]))
                else:
                    lcc.log_info("'erc20_deposit_topic' has correct format: hex")
                with this_dict(sidechain_config["fines"]):
                    if check_that("fines", sidechain_config["fines"], has_length(1)):
                        check_that_entry("generate_eth_address", is_(-10), quiet=True)
                check_that_entry("waiting_blocks", is_integer(), quiet=True)

    def check_erc20_config(self, erc20_config, erc20_methods):
        with this_dict(erc20_config):
            if check_that("erc20_config", erc20_config, has_length(6)):
                if not self.validator.is_hex(erc20_config["contract_code"]):
                    lcc.log_error(
                        "Wrong format of 'contract_code', got: {}".format(erc20_config["contract_code"]))
                else:
                    lcc.log_info("'contract_code' has correct format: hex")
                check_that_entry("create_token_fee", is_integer(), quiet=True)
                if not self.validator.is_hex(erc20_config["transfer_topic"]):
                    lcc.log_error("Wrong format of 'transfer_topic', got: {}".format(erc20_config["transfer_topic"]))
                else:
                    lcc.log_info("'transfer_topic' has correct format: hex")
                for i in range(len(erc20_methods)):
                    if check_that_entry([erc20_methods[i]], has_length(2)):
                        with this_dict(erc20_config[erc20_methods[i]]):
                            if not self.validator.is_hex(erc20_config[erc20_methods[i]]["method"]):
                                lcc.log_error(
                                    "Wrong format of '{}', got: {}".format(erc20_methods[i],
                                                                           erc20_config[erc20_methods[i]]))
                            else:
                                lcc.log_info("'{}' has correct format: hex".format(erc20_methods[i]))
                            check_that_entry("gas", is_integer(), quiet=True)

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Check all fields in global properties")
    def method_main_check(self):
        all_checking_operations = []
        fee_with_price_per_kbyte_operations = ["account_update", "asset_update", "proposal_create", "proposal_update",
                                               "custom", "account_address_create"]
        only_fee_operations = ["transfer", "limit_order_create", "limit_order_cancel", "call_order_update",
                               "account_whitelist", "account_transfer", "asset_update_bitasset",
                               "asset_update_feed_producers", "asset_issue", "asset_reserve", "asset_fund_fee_pool",
                               "asset_settle", "asset_global_settle", "asset_publish_feed", "proposal_delete",
                               "withdraw_permission_create", "withdraw_permission_update", "withdraw_permission_claim",
                               "withdraw_permission_delete", "committee_member_create", "committee_member_update",
                               "committee_member_update_global_parameters", "vesting_balance_create",
                               "vesting_balance_withdraw", "assert", "override_transfer", "asset_claim_fees",
                               "bid_collateral", "create_contract", "call_contract", "contract_transfer",
                               "change_sidechain_config", "transfer_to_address_operation",
                               "generate_eth_address_operation", "create_eth_address_operation", "deposit_eth_address",
                               "withdraw_eth", "approve_widthdraw_eth", "contract_fund_pool", "contract_whitelist",
                               "sidechain_issue", "sidechain_burn", "deposit_erc20_token", "withdraw_erc20_token",
                               "approve_erc20_token_withdraw", "contract_update"]
        no_fee_operations = ["fill_order", "asset_settle_cancel", "balance_claim", "execute_bid"]
        account_create_fee_operations = ["account_create"]
        account_update_fee_operations = ["account_upgrade"]
        asset_create_fee_operations = ["asset_create"]
        pool_fee_operations = ["register_erc20_token"]

        lcc.set_step("Get global properties")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_global_properties'")

        lcc.set_step("Check main fields")
        with this_dict(response["result"]):
            if check_that("global_properties", response["result"], has_length(4)):
                if not self.validator.is_global_object_id(response["result"]["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(response["result"]["id"]))
                else:
                    lcc.log_info("'id' has correct format: global_property_object_type")
                check_that_entry("parameters", is_dict(), quiet=True)
                check_that_entry("next_available_vote_id", is_integer(), quiet=True)
                check_that_entry("active_committee_members", is_list(), quiet=True)

        lcc.set_step("Check global parameters: 'current_fees' field")
        parameters = response["result"]["parameters"]
        with this_dict(parameters):
            if check_that("parameters", parameters, has_length(30)):
                check_that_entry("current_fees", is_dict(), quiet=True)
                check_that_entry("block_interval", is_integer(), quiet=True)
                check_that_entry("maintenance_interval", is_integer(), quiet=True)
                check_that_entry("maintenance_duration_seconds", is_integer(), quiet=True)
                check_that_entry("committee_proposal_review_period", is_integer(), quiet=True)
                check_that_entry("maximum_transaction_size", is_integer(), quiet=True)
                check_that_entry("maximum_block_size", is_integer(), quiet=True)
                check_that_entry("maximum_time_until_expiration", is_integer(), quiet=True)
                check_that_entry("maximum_proposal_lifetime", is_integer(), quiet=True)
                check_that_entry("maximum_asset_whitelist_authorities", is_integer(), quiet=True)
                check_that_entry("maximum_asset_feed_publishers", is_integer(), quiet=True)
                check_that_entry("maximum_committee_count", is_integer(), quiet=True)
                check_that_entry("maximum_authority_membership", is_integer(), quiet=True)
                check_that_entry("reserve_percent_of_fee", is_integer(), quiet=True)
                check_that_entry("network_percent_of_fee", is_integer(), quiet=True)
                check_that_entry("lifetime_referrer_percent_of_fee", is_integer(), quiet=True)
                check_that_entry("cashback_vesting_period_seconds", is_integer(), quiet=True)
                check_that_entry("cashback_vesting_threshold", is_integer(), quiet=True)
                check_that_entry("count_non_member_votes", is_bool(), quiet=True)
                check_that_entry("allow_non_member_whitelists", is_bool(), quiet=True)
                check_that_entry("max_predicate_opcode", is_integer(), quiet=True)
                check_that_entry("fee_liquidation_threshold", is_integer(), quiet=True)
                check_that_entry("accounts_per_fee_scale", is_integer(), quiet=True)
                check_that_entry("account_fee_scale_bitshifts", is_integer(), quiet=True)
                check_that_entry("max_authority_depth", is_integer(), quiet=True)
                check_that_entry("echorand_config", is_dict(), quiet=True)
                check_that_entry("sidechain_config", is_dict(), quiet=True)
                check_that_entry("erc20_config", is_dict(), quiet=True)
                check_that_entry("gas_price", is_dict(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)

        lcc.set_step("Check global parameters: 'current_fees' field")
        current_fees = parameters["current_fees"]
        with this_dict(current_fees):
            if check_that("current_fees", current_fees, has_length(2)):
                check_that_entry("parameters", is_list(), quiet=True)
                check_that_entry("scale", is_integer(), quiet=True)

        lcc.set_step("Check the count of fees for operations")
        fee_parameters = current_fees["parameters"]
        require_that(
            "count of fees for operations",
            fee_parameters, has_length(len(self.all_operations))
        )

        lcc.set_step("Check that count of checking fees fields equal to all operations")
        checking_operations_fee_types = [fee_with_price_per_kbyte_operations, only_fee_operations, no_fee_operations,
                                         account_create_fee_operations, account_update_fee_operations,
                                         asset_create_fee_operations, pool_fee_operations]
        for fee_type in checking_operations_fee_types:
            all_checking_operations.extend(fee_type)
        check_that("'length of checking fees fields equal to all operations'", all_checking_operations,
                   has_length(len(self.all_operations)))

        lcc.set_step("Save the number of types of current_fees")
        for fee_parameter in fee_parameters:
            parameter = fee_parameter[1]
            if len(parameter) == 0:
                self.no_fee_count += 1
                continue
            if len(parameter) == 1 and "fee" in parameter:
                self.only_fee_count += 1
                continue
            if len(parameter) == 2 and ("fee" and "price_per_kbyte") in parameter:
                self.fee_with_price_per_kbyte_count += 1
                continue
            if len(parameter) == 2 and ("membership_annual_fee" and "membership_lifetime_fee") in parameter:
                self.account_update_fee_count += 1
                continue
            if len(parameter) == 2 and ("fee" and "pool_fee") in parameter:
                self.pool_fee_count += 1
                continue
            if len(parameter) == 3 and ("basic_fee" and "premium_fee" and "price_per_kbyte") in parameter:
                self.account_create_fee_count += 1
                continue
            if len(parameter) == 4 and (
                    "symbol3" and "symbol4" and "long_symbol" and "price_per_kbyte") in parameter:
                self.asset_create_count += 1
                continue
            else:
                lcc.log_warn("Warn: Added new option for calculating fee for the operation, got: '{}'".format(
                    fee_parameter))

        lcc.set_step("Check 'fee_with_price_per_kbyte' for operations")
        check_that("'fee_with_price_per_kbyte' operation count", fee_with_price_per_kbyte_operations,
                   has_length(self.fee_with_price_per_kbyte_count))
        self.check_default_fee_for_operation(fee_parameters, fee_with_price_per_kbyte_operations,
                                             self.fee_with_price_per_kbyte)

        lcc.set_step("Check 'only_fee' for operations")
        check_that("'only_fee' operation count", only_fee_operations, has_length(self.only_fee_count))
        self.check_default_fee_for_operation(fee_parameters, only_fee_operations, self.only_fee)

        lcc.set_step("Check 'no_fee' for operations")
        check_that("'no_fee' operation count", no_fee_operations, has_length(self.no_fee_count))
        self.check_default_fee_for_operation(fee_parameters, no_fee_operations, self.no_fee)

        lcc.set_step("Check 'account_create_fee' for operations")
        check_that("'account_create_fee' operation count", account_create_fee_operations,
                   has_length(self.account_create_fee_count))
        self.check_default_fee_for_operation(fee_parameters, account_create_fee_operations, self.account_create_fee)

        lcc.set_step("Check 'account_update_fee' for operations")
        check_that("'account_update_fee' operation count", account_update_fee_operations,
                   has_length(self.account_update_fee_count))
        self.check_default_fee_for_operation(fee_parameters, account_update_fee_operations, self.account_update_fee)

        lcc.set_step("Check 'asset_create_fee' for operations")
        check_that("'asset_create_fee' operation count", asset_create_fee_operations,
                   has_length(self.asset_create_count))
        self.check_default_fee_for_operation(fee_parameters, asset_create_fee_operations, self.asset_create_fee)

        lcc.set_step("Check 'pool_fee' for operations")
        check_that("'pool_fee' operation count", pool_fee_operations,
                   has_length(self.pool_fee_count))
        self.check_default_fee_for_operation(fee_parameters, pool_fee_operations, self.pool_fee)

        lcc.set_step("Check global parameters: 'echorand_config' field")
        echorand_config = parameters["echorand_config"]
        with this_dict(echorand_config):
            if check_that("echorand_config", echorand_config, has_length(7)):
                check_that_entry("_time_net_1mb", is_integer(), quiet=True)
                check_that_entry("_time_net_256b", is_integer(), quiet=True)
                check_that_entry("_creator_count", is_integer(), quiet=True)
                check_that_entry("_verifier_count", is_integer(), quiet=True)
                check_that_entry("_ok_threshold", is_integer(), quiet=True)
                check_that_entry("_max_bba_steps", is_integer(), quiet=True)
                check_that_entry("_gc1_delay", is_integer(), quiet=True)

        lcc.set_step("Check global parameters: 'sidechain_config' field")
        sidechain_config = parameters["sidechain_config"]
        eth_params = ["eth_contract_address", "eth_committee_updated_topic", "eth_gen_address_topic",
                      "eth_deposit_topic", "eth_withdraw_topic"]
        eth_methods = ["eth_committee_update_method", "eth_gen_address_method", "eth_withdraw_method",
                       "eth_update_addr_method", "eth_withdraw_token_method", "eth_collect_tokens_method"]
        self.check_sidechain_config(sidechain_config, eth_params, eth_methods)

        lcc.set_step("Check global parameters: 'erc20_config' field")
        erc20_config = parameters["erc20_config"]
        erc20_methods = ["check_balance_method", "burn_method", "issue_method"]
        self.check_erc20_config(erc20_config, erc20_methods)

        lcc.set_step("Check global parameters: 'gas_price' field")
        gas_price = parameters["gas_price"]
        with this_dict(gas_price):
            if check_that("gas_price", gas_price, has_length(2)):
                check_that_entry("price", is_integer(), quiet=True)
                check_that_entry("gas_amount", is_integer(), quiet=True)


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_global_properties")
@lcc.suite("Negative testing of method 'get_global_properties'", rank=2)
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
    @lcc.depends_on("DatabaseApi.GetGlobalProperties.GetGlobalProperties.method_main_check")
    def call_method_with_params(self, get_all_random_types):
        lcc.set_step("Call method with all types of params")
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-680"
            if i == 4:
                continue
            response_id = self.send_request(self.get_request("get_global_properties", random_values[i]),
                                            self.__api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_global_properties' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True
            )
