# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import is_, check_that, check_that_in, is_str, is_integer, equal_to, is_true, is_none, \
    is_list, is_dict

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
        response = self.get_response(response_id)

        lcc.set_step("Check get objects 'account' and 'asset'")
        check_that(
            "'account' and 'asset'",
            response["result"],
            is_list(self.get_expected("get_objects")),
        )

    @lcc.test("Set subscribe callback")
    def test_set_subscribe_callback(self):
        lcc.set_step("Set subscribe callback")
        params = [123, False]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params=params),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set subscribe callback")
        check_that(
            "'subscribe callback'",
            response["result"],
            is_none(),
        )

    @lcc.test("Set pending transaction callback")
    @lcc.disabled()
    def test_set_pending_transaction_callback(self):
        lcc.set_step("Set pending transaction callback")
        param = [123]
        response_id = self.send_request(self.get_request("set_pending_transaction_callback", params=param),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set pending transaction callback")
        check_that(
            "'pending transaction callback'",
            response["result"],
            is_none(),
        )

    @lcc.test("Set block applied callback")
    @lcc.disabled()
    def test_set_block_applied_callback(self):
        lcc.set_step("Set block applied callback")
        param = [123]
        response_id = self.send_request(self.get_request("set_block_applied_callback", params=param),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check set block applied callback")
        check_that(
            "'block applied callback'",
            response["result"],
            is_none(),
        )

    @lcc.test("Cancel all subscriptions")
    def test_cancel_all_subscriptions(self):
        lcc.set_step("Cancel all subscriptions")
        response_id = self.send_request(self.get_request("cancel_all_subscriptions"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Cancel all subscriptions")
        check_that(
            "'cancel all subscriptions'",
            response["result"],
            is_none(),
        )

    @lcc.test("Get block")
    def test_get_block(self):
        lcc.set_step("Retrieve a full, signed block")
        response_id = self.send_request(self.get_request("get_block"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check block info")
        check_that(
            "'block info'",
            response["result"],
            is_dict(self.get_expected("get_block")),
        )

    @lcc.test("Get block header")
    def test_get_block_header(self):
        lcc.set_step("Retrieve header of signed block")
        response_id = self.send_request(self.get_request("get_block_header"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check block header info")
        check_that(
            "'block header info'",
            response["result"],
            is_dict(self.get_expected("get_block_header")),
        )

    @lcc.test("Get transaction")
    def test_get_transaction(self):
        lcc.set_step("Retrieve transaction")
        response_id = self.send_request(self.get_request("get_transaction"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check transaction info")
        check_that(
            "'transaction info'",
            response["result"],
            is_dict(self.get_expected("get_transaction")),
        )

    @lcc.test("Get recent transaction by id")
    @lcc.hidden()
    def test_get_recent_transaction_by_id(self, trans_id):
        pass

    @lcc.test("Get chain properties")
    def test_get_chain_properties(self):
        lcc.set_step("Get chain properties")
        response_id = self.send_request(self.get_request("get_chain_properties"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check chain properties info")
        check_that(
            "'chain properties'",
            response["result"],
            is_dict(self.get_expected("get_chain_properties")),
        )

    @lcc.test("Get global properties")
    def test_get_global_properties(self):
        lcc.set_step("Get global properties")
        response_id = self.send_request(self.get_request("get_global_properties"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check global properties info")
        check_that(
            "'global properties'",
            response["result"],
            is_dict(self.get_expected("get_global_properties")),
        )

    @lcc.test("Get config")
    def test_get_config(self):
        lcc.set_step("Get config")
        response_id = self.send_request(self.get_request("get_config"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check config info")
        check_that(
            "'config'",
            response["result"],
            is_dict(self.get_expected("get_config")),
        )

    @lcc.test("Get chain id")
    def test_get_chain_id(self):
        lcc.set_step("Get chain id")
        response_id = self.send_request(self.get_request("get_chain_id"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check chain id info")
        check_that(
            "'chain id'",
            response["result"],
            is_str(self.get_expected("get_chain_id")),
        )

    @lcc.test("Get dynamic global properties")
    def test_get_dynamic_global_properties(self):
        lcc.set_step("Get dynamic global properties")
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check dynamic global properties info")
        check_that_in(
            response["result"],
            "id", is_str("2.1.0"),
        )

    @lcc.test("Get key references")
    def test_get_key_references(self):
        lcc.set_step("Get key references")
        response_id = self.send_request(self.get_request("get_key_references"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check key references")
        check_that(
            "'key references'",
            response["result"],
            is_list(self.get_expected("get_key_references")),
        )

    @lcc.test("Get accounts")
    def test_get_accounts(self):
        lcc.set_step("Get accounts")
        response_id = self.send_request(self.get_request("get_accounts"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check accounts")
        check_that(
            "'accounts'",
            response["result"],
            is_list(self.get_expected("get_accounts")),
        )

    @lcc.test("Get full accounts by ids")
    def test_get_full_accounts_ids(self):
        lcc.set_step("Get full accounts by ids")
        params = [["1.2.6", "1.2.7", "1.2.8", "1.2.9", "1.2.10", "1.2.11", "1.2.14"], False]
        response_id = self.send_request(self.get_request("get_full_accounts", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check full accounts by ids")
        check_that(
            "'full accounts by ids'",
            response["result"],
            is_list(self.get_expected("get_full_accounts_ids")),
        )

    @lcc.test("Get full accounts by names")
    def test_get_full_accounts_names(self):
        lcc.set_step("Get full accounts by names")
        params = [["init0", "init1", "init2", "init3", "init4", "init5", "nathan", "test124"], False]
        response_id = self.send_request(self.get_request("get_full_accounts", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check full accounts by names")
        check_that(
            "'full accounts by names'",
            response["result"],
            is_list(self.get_expected("get_full_accounts_names")),
        )

    @lcc.test("Get account by name")
    def test_get_account_by_name(self):
        lcc.set_step("Get account by name")
        response_id = self.send_request(self.get_request("get_account_by_name"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check account by name")
        check_that(
            "'init2'",
            response["result"],
            is_dict(self.get_expected("get_account_by_name")),
        )

    @lcc.test("Get account references")
    @lcc.tags("don't work")
    def test_get_account_references(self):
        lcc.set_step("Get account references")
        # todo нет необходимого аккаунта для проверки
        response_id = self.send_request(self.get_request("get_account_references"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check account references")
        check_that(
            "'1.2.28'",
            response["result"],
            is_(self.get_expected("get_account_references")),
        )

    @lcc.test("Lookup account names")
    def test_lookup_account_names(self):
        lcc.set_step("Lookup account names")
        response_id = self.send_request(self.get_request("lookup_account_names"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup account names")
        check_that(
            "'lookup account names'",
            response["result"],
            is_list(self.get_expected("lookup_account_names")),
        )

    @lcc.test("Lookup accounts")
    def test_lookup_accounts(self):
        lcc.set_step("Lookup accounts")
        # todo непонятно как работает limit
        response_id = self.send_request(self.get_request("lookup_accounts"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup accounts")
        check_that(
            "'lookup accounts'",
            response["result"],
            is_list(self.get_expected("lookup_accounts")),
        )

    @lcc.test("Get account count")
    def test_get_account_count(self):
        lcc.set_step("Get account count")
        response_id = self.send_request(self.get_request("get_account_count"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get account count")
        check_that(
            "'account count'",
            response["result"],
            is_integer(29)
        )

    @lcc.test("Get account balances, empty param: assets")
    def test_get_account_balances_empty_assets(self):
        lcc.set_step("Get account balances")
        params = ["1.2.8", []]
        response_id = self.send_request(self.get_request("get_account_balances", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get account balances")
        check_that(
            "'account balances'",
            response["result"],
            is_list(self.get_expected("get_account_balances_empty")),
        )

    @lcc.test("Get account balances")
    def test_get_account_balances(self):
        lcc.set_step("Get account balances")
        params = ["1.2.8", ["1.3.0", "1.3.1", "1.3.2"]]
        response_id = self.send_request(self.get_request("get_account_balances", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get account balances")
        check_that(
            "'account balances'",
            response["result"],
            is_list(self.get_expected("get_account_balances")),
        )

    @lcc.test("Get named account balances, empty param: assets")
    def test_get_named_account_balances_empty_assets(self):
        lcc.set_step("Get named account balances")
        params = ["init2", []]
        response_id = self.send_request(self.get_request("get_named_account_balances", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get named account balances")
        check_that(
            "'named account balances'",
            response["result"],
            is_list(self.get_expected("get_account_balances_empty")),
        )

    @lcc.test("Get named account balances")
    def test_get_named_account_balances(self):
        lcc.set_step("Get named account balances")
        params = ["init2", ["1.3.0", "1.3.1", "1.3.2"]]
        response_id = self.send_request(self.get_request("get_named_account_balances", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get named account balances")
        check_that(
            "'named account balances'",
            response["result"],
            is_list(self.get_expected("get_account_balances")),
        )

    @lcc.test("Get balance objects")
    @lcc.hidden()
    def test_get_balance_objects(self, addrs):
        pass

    @lcc.test("Get vested balances")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_get_vested_balances(self):
        # todo нет нужных balance_ids
        lcc.set_step("Get vested balances")
        response_id = self.send_request(self.get_request("get_vested_balances"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get vested balances")
        check_that(
            "'vested balances'",
            response["result"],
            is_(self.get_expected("get_account_balances")),
        )

    @lcc.test("Get vesting balances")
    @lcc.hidden()
    def test_get_vesting_balances(self, account_id):
        pass

    @lcc.test("Get assets")
    def test_get_assets(self):
        lcc.set_step("Get assets")
        response_id = self.send_request(self.get_request("get_assets"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get assets")
        check_that(
            "'assets'",
            response["result"],
            is_list(self.get_expected("get_assets")),
        )

    @lcc.test("List assets")
    def test_list_assets(self):
        lcc.set_step("List assets")
        # todo чувствителен к регистру
        response_id = self.send_request(self.get_request("list_assets"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check list assets")
        check_that(
            "'list assets'",
            response["result"],
            is_list(self.get_expected("list_assets")),
        )

    @lcc.test("Lookup asset symbols")
    def test_lookup_asset_symbols(self):
        lcc.set_step("Lookup asset symbols")
        params = [["ECHO", "ECHOTEST"]]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup asset symbols")
        check_that(
            "'lookup asset symbols'",
            response["result"],
            is_list(self.get_expected("lookup_asset_symbols")),
        )

    @lcc.test("Lookup asset ids")
    def test_lookup_asset_symbols_ids(self):
        lcc.set_step("Lookup asset ids")
        params = [["ECHO", "ECHOTEST"]]
        response_id = self.send_request(self.get_request("lookup_asset_symbols", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup asset ids")
        check_that(
            "'lookup asset ids'",
            response["result"],
            is_list(self.get_expected("lookup_asset_symbols")),
        )

    @lcc.test("Get order book")
    @lcc.hidden()
    def test_get_order_book(self, base, quote, depth=50):
        pass

    @lcc.test("Get limit orders")
    @lcc.hidden()
    def test_get_limit_orders(self, a, b, limit):
        pass

    @lcc.test("Get call orders")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_get_call_orders(self):
        lcc.set_step("Get call orders")
        response_id = self.send_request(self.get_request("get_call_orders"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get call orders")
        check_that(
            "'call orders'",
            response["result"],
            is_(self.get_expected("get_call_orders")),
        )

    @lcc.test("Get settle orders")
    @lcc.tags("empty data receive")
    def test_get_settle_orders(self):
        lcc.set_step("Get settle orders")
        response_id = self.send_request(self.get_request("get_settle_orders"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get settle orders")
        check_that(
            "'settle orders'",
            response["result"],
            is_(self.get_expected("get_settle_orders")),
        )

    @lcc.test("Get margin positions")
    @lcc.tags("empty data receive")
    def test_get_margin_positions(self):
        lcc.set_step("Get margin positions")
        response_id = self.send_request(self.get_request("get_margin_positions"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get margin positions")
        check_that(
            "'margin positions'",
            response["result"],
            is_(self.get_expected("get_margin_positions")),
        )

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
        response = self.get_response(response_id)

        lcc.set_step("Check get witnesses")
        check_that_in(
            response["result"][0],
            "id", is_str("1.6.0"),
            "witness_account", is_str("1.2.0"),
            "last_aslot", is_integer(),
            "signing_key", is_str("ECHO1111111111111111111111111111111114T1Anm"),
            "pay_vb", is_str("1.13.1"),
            "vote_id", is_str("1:0"),
            "total_votes", is_integer(0),
            "url", is_str(""),
            "total_missed", is_integer(0),
            "last_confirmed_block_num", is_integer(),
            "ed_signing_key", is_str("0000000000000000000000000000000000000000000000000000000000000000")
        )

    @lcc.test("Get witness by account")
    def test_get_witness_by_account(self):
        lcc.set_step("Get witness by account")
        response_id = self.send_request(self.get_request("get_witness_by_account"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check witness by account")
        check_that_in(
            response["result"],
            "id", is_str("1.6.0"),
            "witness_account", is_str("1.2.0"),
            "last_aslot", is_integer(),
            "signing_key", is_str("ECHO1111111111111111111111111111111114T1Anm"),
            "pay_vb", is_str("1.13.1"),
            "vote_id", is_str("1:0"),
            "total_votes", is_integer(0),
            "url", is_str(""),
            "total_missed", is_integer(0),
            "last_confirmed_block_num", is_integer(),
            "ed_signing_key", is_str("0000000000000000000000000000000000000000000000000000000000000000")
        )

    @lcc.test("Check return result methods 'get_witnesses' and 'get_witness_by_account'")
    def test_return_result(self):
        lcc.set_step("Get witnesses use 'get_witnesses'")
        response_id = self.send_request(self.get_request("get_witnesses"), self.__api_identifier)
        resp1 = self.get_response(response_id)

        lcc.set_step("Get witnesses use 'get_witness_by_account'")
        response_id = self.send_request(self.get_request("get_witness_by_account"), self.__api_identifier)
        resp2 = self.get_response(response_id)

        lcc.set_step("Check return result methods 'get_witnesses' and 'get_witness_by_account'")
        check_that(
            "test",
            resp1["result"][0], equal_to(resp2["result"])
        )

    @lcc.test("Lookup witness accounts")
    def test_lookup_witness_accounts(self):
        lcc.set_step("Lookup witness accounts")
        response_id = self.send_request(self.get_request("lookup_witness_accounts"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup witness accounts")
        check_that(
            "'lookup witness accounts'",
            response["result"],
            is_list(self.get_expected("lookup_witness_accounts")),
        )

    @lcc.test("Get witness count")
    def test_get_witness_count(self):
        lcc.set_step("Get witness count")
        response_id = self.send_request(self.get_request("get_witness_count"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get witness count")
        check_that(
            "'witness count'",
            response["result"],
            is_integer(1)
        )

    @lcc.test("Get committee members")
    def test_get_committee_members(self):
        lcc.set_step("Get committee members")
        response_id = self.send_request(self.get_request("get_committee_members"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get committee members")
        check_that(
            "'committee members'",
            response["result"],
            is_list(self.get_expected("get_committee_members")),
        )

    @lcc.test("Get committee members by account")
    def test_get_committee_member_by_account(self):
        lcc.set_step("Get committee members by account")
        response_id = self.send_request(self.get_request("get_committee_member_by_account"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get committee members by account")
        check_that(
            "'committee members by account'",
            response["result"],
            is_dict(self.get_expected("get_committee_member_by_account")),
        )

    @lcc.test("Lookup committee member by accounts")
    def test_lookup_committee_member_accounts(self):
        lcc.set_step("Lookup committee member by accounts")
        response_id = self.send_request(self.get_request("lookup_committee_member_accounts"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup committee member by accounts")
        check_that(
            "'lookup committee member by accounts'",
            response["result"],
            is_list(self.get_expected("lookup_committee_member_accounts")),
        )

    @lcc.test("Get workers by account")
    @lcc.tags("empty data receive")
    def test_get_workers_by_account(self):
        lcc.set_step("Get workers by account")
        response_id = self.send_request(self.get_request("get_workers_by_account"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get workers by account")
        check_that(
            "'workers by account'",
            response["result"],
            is_(self.get_expected("get_workers_by_account")),
        )

    @lcc.test("Lookup vote ids")
    def test_lookup_vote_ids(self):
        lcc.set_step("Lookup vote ids")
        response_id = self.send_request(self.get_request("lookup_vote_ids"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check lookup vote ids")
        check_that(
            "'lookup vote ids'",
            response["result"],
            is_list(self.get_expected("lookup_vote_ids")),
        )

    @lcc.test("Get transaction hex")
    def test_get_transaction_hex(self):
        lcc.set_step("Get transaction hex")
        response_id = self.send_request(self.get_request("get_transaction_hex", [self.get_expected("get_transaction")]),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get transaction hex")
        check_that(
            "'transaction hex'",
            response["result"],
            is_str(self.get_expected("get_transaction_hex")),
        )

    @lcc.test("Get required signatures")
    def test_get_required_signatures(self):
        lcc.set_step("Get potential signatures")
        response_id = self.send_request(
            self.get_request("get_required_signatures", [self.get_expected("get_transaction"),
                                                         ["ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"]]),
            self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get potential signatures")
        check_that(
            "'potential signatures'",
            response["result"],
            is_list(["ECHO6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"]),
        )

    @lcc.test("Get potential signatures")
    def test_get_potential_signatures(self):
        lcc.set_step("Get potential signatures")
        response_id = self.send_request(
            self.get_request("get_potential_signatures", [self.get_expected("get_transaction")]),
            self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get potential signatures")
        check_that(
            "'potential signatures'",
            response["result"],
            is_list(self.get_expected("get_potential_signatures")),
        )

    @lcc.test("Get potential address signatures")
    @lcc.tags("empty data receive")
    def test_get_potential_address_signatures(self):
        lcc.set_step("Get potential address signatures")
        response_id = self.send_request(self.get_request("get_potential_address_signatures",
                                                         [self.get_expected("get_transaction")]),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get potential address signatures")
        check_that(
            "'potential address signatures'",
            response["result"],
            is_(self.get_expected("get_potential_address_signatures")),
        )

    @lcc.test("Verify authority")
    def test_verify_authority(self):
        lcc.set_step("Verify authority")
        response_id = self.send_request(self.get_request("verify_authority", [self.get_expected("get_transaction")]),
                                        self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check verify authority")
        check_that(
            "'verify authority'",
            response["result"],
            is_true(),
        )

    @lcc.test("Verify account authority")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_verify_account_authority(self):
        lcc.set_step("Verify account authority")
        params = ["1.2.12", []]
        response_id = self.send_request(self.get_request("verify_account_authority", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check verify account authority")
        check_that(
            "'verify account authority'",
            response["result"],
            is_true(),
        )

    @lcc.test("Validate transaction")
    @lcc.tags("don't work")
    @lcc.disabled()
    def test_validate_transaction(self):
        lcc.set_step("Validate transaction")
        response_id = self.send_request(
            self.get_request("validate_transaction", [self.get_expected("get_transaction")]),
            self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check validate transaction")
        check_that(
            "'validate transaction'",
            response["result"],
            is_true(),
        )

    @lcc.test("Get required fees")
    @lcc.tags("aa")
    def test_get_required_fees(self):
        lcc.set_step("Get required fees")
        params = [self.get_expected("contract_operations"), "1.3.0"]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get required fees")
        check_that(
            "'required fees'",
            response["result"],
            is_(self.get_expected("get_required_fees")),
        )

    @lcc.test("Get proposed transactions")
    @lcc.tags("empty data receive")
    def test_get_proposed_transactions(self):
        lcc.set_step("Get proposed transactions")
        response_id = self.send_request(self.get_request("get_proposed_transactions", ), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get proposed transactions")
        check_that(
            "'proposed transactions'",
            response["result"],
            is_(self.get_expected("get_proposed_transactions")),
        )

    @lcc.test("Get all contracts")
    def test_get_all_contracts(self):
        lcc.set_step("Get all contracts")
        response_id = self.send_request(self.get_request("get_all_contracts"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get all contracts")
        check_that(
            "'all contracts'",
            response["result"],
            is_(self.get_expected("get_all_contracts")),
        )

    @lcc.test("Get contract logs")
    def test_get_contract_logs(self):
        lcc.set_step("Get contract logs")
        response_id = self.send_request(self.get_request("get_contract_logs"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get contract logs")
        check_that(
            "'contract logs'",
            response["result"],
            is_(self.get_expected("get_contract_logs")),
        )

    @lcc.test("Subscribe contract logs")
    @lcc.hidden()
    def test_subscribe_contract_logs(self, callback, contract_id, _from, to):
        pass

    @lcc.test("Get contract result")
    def test_get_contract_result(self):
        lcc.set_step("Get contract result")
        response_id = self.send_request(self.get_request("get_contract_result"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get contract result")
        check_that(
            "'contract result'",
            response["result"],
            is_(self.get_expected("get_contract_result")),
        )

    @lcc.test("Get contract")
    def test_get_contract(self):
        lcc.set_step("Get contract")
        response_id = self.send_request(self.get_request("get_contract"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get contract")
        check_that(
            "'contract'",
            response["result"],
            is_(self.get_expected("get_contract")),
        )

    @lcc.test("Call contract no changing state")
    def test_call_contract_no_changing_state(self):
        lcc.set_step("Get contract")
        response_id = self.send_request(self.get_request("call_contract_no_changing_state"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check call contract no changing state")
        check_that(
            "'method call'",
            response["result"],
            is_str("000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000"
                   "0000000000000000000000000000000e48656c6c6f20576f726c64212121000000000000000000000000000000000000"),
        )

    @lcc.test("Get contracts")
    def test_get_contracts(self):
        lcc.set_step("Get contracts")
        response_id = self.send_request(self.get_request("get_contracts"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get contracts")
        check_that(
            "'contracts'",
            response["result"],
            is_(self.get_expected("get_contracts")),
        )

    @lcc.test("Get contract balances")
    def test_get_contract_balances(self):
        lcc.set_step("Get contract balances")
        response_id = self.send_request(self.get_request("get_contract_balances"), self.__api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check get contract balances")
        check_that(
            "'contract balances'",
            response["result"],
            is_(self.get_expected("get_contract_balances")),
        )
