# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Check all the methods belonging to the database_api"
}


@lcc.suite("Testing 'Database API' methods call")
@lcc.hidden()
class DatabaseApi(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")
        lcc.log_info(
            "Database API identifiers is '{}'".format(self.__api_identifier))

    @lcc.test("Get objects")
    def test_get_objects(self):
        lcc.set_step("Get objects 'account' and 'asset'")
        response_id = self.send_request(self.get_request("get_objects"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Set subscribe callback")
    def test_set_subscribe_callback(self):
        lcc.set_step("Set subscribe callback")
        params = [123, False]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params=params),
                                        self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Set pending transaction callback")
    def test_set_pending_transaction_callback(self):
        lcc.set_step("Set pending transaction callback")
        param = [123]
        response_id = self.send_request(self.get_request("set_pending_transaction_callback", params=param),
                                        self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Set block applied callback")
    def test_set_block_applied_callback(self):
        lcc.set_step("Set block applied callback")
        param = [123]
        response_id = self.send_request(self.get_request("set_block_applied_callback", params=param),
                                        self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Cancel all subscriptions")
    def test_cancel_all_subscriptions(self):
        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get block")
    def test_get_block(self):
        lcc.set_step("Retrieve a full, signed block")
        response_id = self.send_request(self.get_request("get_block"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get block header")
    def test_get_block_header(self):
        lcc.set_step("Retrieve header of signed block")
        response_id = self.send_request(self.get_request("get_block_header"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        lcc.set_step("Retrieve transaction")
        response_id = self.send_request(self.get_request("get_transaction"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get recent transaction by id")
    def test_get_recent_transaction_by_id(self, trans_id):
        pass

    @lcc.test("Get chain properties")
    def test_get_chain_properties(self):
        lcc.set_step("Get chain properties")
        response_id = self.send_request(self.get_request("get_chain_properties"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get global properties")
    def test_get_global_properties(self):
        lcc.set_step("Get global properties")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get config")
    def test_get_config(self):
        lcc.set_step("Get config")
        response_id = self.send_request(self.get_request("get_config"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get chain id")
    def test_get_chain_id(self):
        lcc.set_step("Get chain id")
        response_id = self.send_request(self.get_request("get_chain_id"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get dynamic global properties")
    def test_get_dynamic_global_properties(self):
        lcc.set_step("Get dynamic global properties")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get key references")
    def test_get_key_references(self):
        lcc.set_step("Get key references")
        response_id = self.send_request(self.get_request("get_key_references"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get accounts")
    def test_get_accounts(self):
        lcc.set_step("Get accounts")
        response_id = self.send_request(self.get_request("get_accounts", [[""]]), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get full accounts by ids")
    def test_get_full_accounts_ids(self):
        lcc.set_step("Get full accounts by ids")
        params = [["1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10", "1.2.11", "1.2.14"], False]
        response_id = self.send_request(self.get_request("get_full_accounts", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get full accounts by names")
    def test_get_full_accounts_names(self):
        lcc.set_step("Get full accounts by names")
        params = [["init0", "init1", "init2", "init3", "init4", "init5", "nathan", "test124"], False]
        response_id = self.send_request(self.get_request("get_full_accounts", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get account by name")
    def test_get_account_by_name(self):
        lcc.set_step("Get account by name")
        response_id = self.send_request(self.get_request("get_account_by_name"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get account references")
    def test_get_account_references(self):
        lcc.set_step("Get account references")
        # todo нет необходимого аккаунта для проверки
        response_id = self.send_request(self.get_request("get_account_references"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup account names")
    def test_lookup_account_names(self):
        lcc.set_step("Lookup account names")
        response_id = self.send_request(self.get_request("lookup_account_names"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup accounts")
    def test_lookup_accounts(self):
        lcc.set_step("Lookup accounts")
        # todo непонятно как работает limit
        response_id = self.send_request(self.get_request("lookup_accounts"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get account count")
    def test_get_account_count(self):
        lcc.set_step("Get account count")
        response_id = self.send_request(self.get_request("get_account_count"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get account balances, empty param: assets")
    def test_get_account_balances_empty_assets(self):
        lcc.set_step("Get account balances")
        params = ["1.2.8", []]
        response_id = self.send_request(self.get_request("get_account_balances", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get account balances")
    def test_get_account_balances(self):
        lcc.set_step("Get account balances")
        params = ["1.2.8", ["1.3.0", "1.3.1", "1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get named account balances, empty param: assets")
    def test_get_named_account_balances_empty_assets(self):
        lcc.set_step("Get named account balances")
        params = ["init2", []]
        response_id = self.send_request(self.get_request("get_named_account_balances", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get named account balances")
    def test_get_named_account_balances(self):
        lcc.set_step("Get named account balances")
        params = ["nathan", []]
        response_id = self.send_request(self.get_request("get_named_account_balances", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get balance objects")
    @lcc.hidden()
    def test_get_balance_objects(self, addrs):
        pass

    @lcc.test("Get vested balances")
    def test_get_vested_balances(self):
        # todo нет нужных balance_ids
        lcc.set_step("Get vested balances")
        response_id = self.send_request(self.get_request("get_vested_balances"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get vesting balances")
    @lcc.hidden()
    def test_get_vesting_balances(self, account_id):
        pass

    @lcc.test("Get assets")
    def test_get_assets(self):
        lcc.set_step("Get assets")
        response_id = self.send_request(self.get_request("get_assets"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("List assets")
    def test_list_assets(self):
        lcc.set_step("List assets")
        # todo чувствителен к регистру
        response_id = self.send_request(self.get_request("list_assets", ["", 100]), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup asset symbols")
    def test_lookup_asset_symbols(self):
        lcc.set_step("Lookup asset symbols")
        params = [["ECHO", "ECHOTEST"]]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup asset ids")
    def test_lookup_asset_symbols_ids(self):
        lcc.set_step("Lookup asset ids")
        params = [["ECHO", "ECHOTEST"]]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get order book")
    @lcc.hidden()
    def test_get_order_book(self, base, quote, depth=50):
        pass

    @lcc.test("Get limit orders")
    @lcc.hidden()
    def test_get_limit_orders(self, a, b, limit):
        pass

    @lcc.test("Get call orders")
    def test_get_call_orders(self):
        lcc.set_step("Get call orders")
        response_id = self.send_request(self.get_request("get_call_orders"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get settle orders")
    def test_get_settle_orders(self):
        lcc.set_step("Get settle orders")
        response_id = self.send_request(self.get_request("get_settle_orders"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get margin positions")
    def test_get_margin_positions(self):
        lcc.set_step("Get margin positions")
        response_id = self.send_request(self.get_request("get_margin_positions"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Subscribe to market")
    @lcc.hidden()
    def test_subscribe_to_market(self, callback, a, b):
        pass

    @lcc.test("Unsubscribe to market")
    @lcc.hidden()
    def test_unsubscribe_from_market(self, a, b):
        pass

    @lcc.test("Get ticker")
    @lcc.hidden()
    def test_get_ticker(self, base, quote):
        pass

    @lcc.test("Get 24 volume")
    @lcc.hidden()
    def test_get_24_volume(self, base, quote):
        pass

    @lcc.test("Get trade history")
    @lcc.hidden()
    def test_get_trade_history(self, base, quote, start, stop, limit=100):
        pass

    @lcc.test("Get witnesses")
    def test_get_witnesses(self):
        lcc.set_step("Get witnesses")
        response_id = self.send_request(self.get_request("get_witnesses"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get witness by account")
    def test_get_witness_by_account(self):
        lcc.set_step("Get witness by account")
        response_id = self.send_request(self.get_request("get_witness_by_account"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Check return result methods 'get_witnesses' and 'get_witness_by_account'")
    def test_return_result(self):
        lcc.set_step("Get witnesses use 'get_witnesses'")
        response_id = self.send_request(self.get_request("get_witnesses"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

        lcc.set_step("Get witnesses use 'get_witness_by_account'")
        response_id = self.send_request(self.get_request("get_witness_by_account"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup witness accounts")
    def test_lookup_witness_accounts(self):
        lcc.set_step("Lookup witness accounts")
        response_id = self.send_request(self.get_request("lookup_witness_accounts"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get witness count")
    def test_get_witness_count(self):
        lcc.set_step("Get witness count")
        response_id = self.send_request(self.get_request("get_witness_count"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get committee members")
    def test_get_committee_members(self):
        lcc.set_step("Get committee members")
        response_id = self.send_request(self.get_request("get_committee_members"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get committee members by account")
    def test_get_committee_member_by_account(self):
        lcc.set_step("Get committee members by account")
        response_id = self.send_request(self.get_request("get_committee_member_by_account"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup committee member by accounts")
    def test_lookup_committee_member_accounts(self):
        lcc.set_step("Lookup committee member by accounts")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get workers by account")
    def test_get_workers_by_account(self):
        lcc.set_step("Get workers by account")
        response_id = self.send_request(self.get_request("get_workers_by_account"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Lookup vote ids")
    def test_lookup_vote_ids(self):
        lcc.set_step("Lookup vote ids")
        response_id = self.send_request(self.get_request("lookup_vote_ids"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get transaction hex")
    def test_get_transaction_hex(self):
        lcc.set_step("Get transaction hex")
        param = []
        response_id = self.send_request(self.get_request("get_transaction_hex", param),
                                        self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get required signatures")
    def test_get_required_signatures(self):
        lcc.set_step("Get potential signatures")
        params = []
        response_id = self.send_request(
            self.get_request("get_required_signatures", params),
            self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get potential signatures")
    def test_get_potential_signatures(self):
        lcc.set_step("Get potential signatures")
        param = []
        response_id = self.send_request(
            self.get_request("get_potential_signatures", param),
            self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get potential address signatures")
    def test_get_potential_address_signatures(self):
        lcc.set_step("Get potential address signatures")
        param = []
        response_id = self.send_request(self.get_request("get_potential_address_signatures", param),
                                        self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Verify authority")
    def test_verify_authority(self):
        lcc.set_step("Verify authority")
        param = []
        response_id = self.send_request(self.get_request("verify_authority", param),
                                        self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Verify account authority")
    def test_verify_account_authority(self):
        lcc.set_step("Verify account authority")
        params = ["1.2.12", []]
        response_id = self.send_request(self.get_request("verify_account_authority", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Validate transaction")
    def test_validate_transaction(self):
        lcc.set_step("Validate transaction")
        param = []
        response_id = self.send_request(
            self.get_request("validate_transaction", param), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get required fees")
    def test_get_required_fees(self):
        lcc.set_step("Get required fees")
        params = ["operation", "1.3.0"]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get proposed transactions")
    def test_get_proposed_transactions(self):
        lcc.set_step("Get proposed transactions")
        response_id = self.send_request(self.get_request("get_proposed_transactions", ), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get all contracts")
    def test_get_all_contracts(self):
        lcc.set_step("Get all contracts")
        response_id = self.send_request(self.get_request("get_all_contracts"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get contract logs")
    def test_get_contract_logs(self):
        lcc.set_step("Get contract logs")
        response_id = self.send_request(self.get_request("get_contract_logs"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Subscribe contract logs")
    @lcc.hidden()
    def test_subscribe_contract_logs(self, callback, contract_id, _from, to):
        pass

    @lcc.test("Get contract result")
    def test_get_contract_result(self):
        lcc.set_step("Get contract result")
        response_id = self.send_request(self.get_request("get_contract_result"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get contract")
    def test_get_contract(self):
        lcc.set_step("Get contract")
        response_id = self.send_request(self.get_request("get_contract"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Call contract no changing state")
    def test_call_contract_no_changing_state(self):
        lcc.set_step("Get contract")
        response_id = self.send_request(self.get_request("call_contract_no_changing_state"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get contracts")
    def test_get_contracts(self):
        lcc.set_step("Get contracts")
        response_id = self.send_request(self.get_request("get_contracts"), self.__api_identifier)
        self.get_response(response_id, log_response=True)

    @lcc.test("Get contract balances")
    def test_get_contract_balances(self):
        lcc.set_step("Get contract balances")
        response_id = self.send_request(self.get_request("get_contract_balances"), self.__api_identifier)
        self.get_response(response_id, log_response=True)
