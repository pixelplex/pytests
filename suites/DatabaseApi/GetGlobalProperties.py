# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_integer, check_that_entry, this_dict, check_that, is_list, \
    require_that, is_, has_length, is_bool, is_dict, has_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_global_properties'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_global_properties")
@lcc.suite("Check work of method 'get_global_properties'", rank=1)
class GetGlobalProperties(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None
        self.all_operations = self.echo.config.operation_ids.__dict__

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
    def fee_with_price_per_output(actual_fee):
        with this_dict(actual_fee):
            if check_that("fee", actual_fee, has_length(2)):
                check_that_entry("fee", is_integer(), quiet=True)
                check_that_entry("price_per_output", is_integer(), quiet=True)

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
            if check_that("sidechain_config", sidechain_config, has_length(9)):
                for i in range(len(eth_params)):
                    if not self.validator.is_hex(sidechain_config[eth_params[i]]):
                        lcc.log_error(
                            "Wrong format of '{}', got: {}".format(eth_params[i], sidechain_config[eth_params[i]]))
                    else:
                        lcc.log_info("'{}' has correct format: hex".format(eth_params[i]))
                for i in range(len(eth_methods)):
                    if check_that_entry([eth_methods[i]], is_dict(), quiet=True):
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

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Check all fields in global properties")
    def method_main_check(self):
        lcc.set_step("Get global properties")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__api_identifier)
        response = self.get_response(response_id, log_response=True)
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
            if check_that("parameters", parameters, has_length(29)):
                check_that_entry("current_fees", is_dict(), quiet=True)
                check_that_entry("block_interval", is_integer(), quiet=True)
                check_that_entry("maintenance_interval", is_integer(), quiet=True)
                check_that_entry("maintenance_skip_slots", is_integer(), quiet=True)
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
                check_that_entry("gas_price", is_dict(), quiet=True)
                check_that_entry("extensions", is_list(), quiet=True)

        lcc.set_step("Check global parameters: 'current_fees' field")
        current_fees = parameters["current_fees"]
        with this_dict(current_fees):
            if check_that("current_fees", current_fees, has_length(2)):
                check_that_entry("parameters", is_list(), quiet=True)
                check_that_entry("scale", is_integer(), quiet=True)

        lcc.set_step("Check the count of fees for operations")
        require_that(
            "count of fees for operations",
            # todo: Delete '-7' when 44 for 50 operations will be added
            len(current_fees["parameters"]), is_(len(self.all_operations) - 7)
        )

        lcc.set_step("Check 'fee_with_price_per_kbyte' for operations")
        operations = ["transfer", "account_update", "asset_update", "asset_issue", "proposal_create",
                      "proposal_update", "withdraw_permission_claim", "custom", "override_transfer"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.fee_with_price_per_kbyte)

        lcc.set_step("Check 'only_fee' for operations")
        operations = ["limit_order_create", "limit_order_cancel", "call_order_update", "account_whitelist",
                      "account_transfer", "asset_update_bitasset", "asset_update_feed_producers", "asset_reserve",
                      "asset_fund_fee_pool", "asset_settle", "asset_global_settle", "asset_publish_feed",
                      "witness_create", "witness_update", "proposal_delete", "withdraw_permission_create",
                      "withdraw_permission_update", "withdraw_permission_delete", "committee_member_create",
                      "committee_member_update", "committee_member_update_global_parameters", "vesting_balance_create",
                      "vesting_balance_withdraw", "worker_create", "assert", "transfer_from_blind", "asset_claim_fees",
                      "bid_collateral", "create_contract", "call_contract", "contract_transfer",
                      "change_sidechain_config"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.only_fee)

        lcc.set_step("Check 'no_fee' for operations")
        operations = ["fill_order", "balance_claim", "asset_settle_cancel", "fba_distribute", "execute_bid"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.no_fee)

        lcc.set_step("Check 'account_create_fee' for operations")
        operations = ["account_create"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.account_create_fee)

        lcc.set_step("Check 'account_update_fee' for operations")
        operations = ["account_upgrade"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.account_update_fee)

        lcc.set_step("Check 'asset_create_fee' for operations")
        operations = ["asset_create"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.asset_create_fee)

        lcc.set_step("Check 'fee_with_price_per_output' for operations")
        operations = ["transfer_to_blind", "blind_transfer"]
        self.check_default_fee_for_operation(current_fees["parameters"], operations, self.fee_with_price_per_output)

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
        eth_methods = ["eth_committee_update_method", "eth_gen_address_method", "eth_withdraw_method"]
        self.check_sidechain_config(sidechain_config, eth_params, eth_methods)

        lcc.set_step("Check global parameters: 'gas_price' field")
        gas_price = parameters["gas_price"]
        with this_dict(gas_price):
            if check_that("gas_price", gas_price, has_length(2)):
                check_that_entry("price", is_integer(), quiet=True)
                check_that_entry("gas_amount", is_integer(), quiet=True)


@lcc.prop("testing", "negative")
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
