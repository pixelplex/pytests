# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError
from lemoncheesecake.matching import this_dict, check_that, has_length, check_that_entry, is_list, has_entry, \
    equal_to, require_that

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract_pool_whitelist'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract_pool_whitelist")
@lcc.suite("Check work of method 'get_contract_pool_whitelist'", rank=1)
class GetContractPoolWhitelist(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.contract = self.get_byte_code("piggy", "code")

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
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}''".format(self.echo_acc0, self.echo_acc1))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract_pool_whitelist'")
    def method_main_check(self, get_random_integer):
        value_to_pool = get_random_integer

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Get a contract's fee pool whitelist")
        response_id = self.send_request(self.get_request("get_contract_pool_whitelist", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contract_pool_whitelist'")
        with this_dict(result):
            if check_that("contract pool whitelist", result, has_length(2)):
                check_that_entry("whitelist", is_list([]))
                check_that_entry("blacklist", is_list([]))

        lcc.set_step("Add one account to whitelist and one account to blacklist")
        whitelist, blacklist = [self.echo_acc0], [self.echo_acc1]
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier, add_to_whitelist=whitelist,
                                                        add_to_blacklist=blacklist, log_broadcast=True)

        lcc.set_step("Get updated a contract's fee pool whitelist")
        response_id = self.send_request(self.get_request("get_contract_pool_whitelist", [contract_id]),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check added accounts to contract lists")
        with this_dict(result):
            if check_that("contract pool whitelist", result, has_length(2)):
                check_that_entry("whitelist", is_list(whitelist))
                check_that_entry("blacklist", is_list(blacklist))


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_contract_pool_whitelist")
@lcc.suite("Positive testing of method 'get_contract_pool_whitelist'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc5 = None
        self.echo_acc6 = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")

    def get_contract_pool_balance(self, contract_id):
        response_id = self.send_request(self.get_request("get_contract_pool_balance", [contract_id]),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"]["amount"]

    def get_contract_pool_whitelist(self, contract_id):
        response_id = self.send_request(self.get_request("get_contract_pool_whitelist", [contract_id]),
                                        self.__database_api_identifier)
        return self.get_response(response_id)["result"]

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
        self.echo_acc5 = self.get_account_id(self.accounts[5], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc6 = self.get_account_id(self.accounts[6], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc5, self.echo_acc6))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check work of add and remove accounts to/from whitelist")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def add_remove_accounts_to_from_whitelist(self):
        full_whitelist = []

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to perform two calls contract 'greet' method")
        operation_method = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                     bytecode=self.greet, callee=contract_id)
        needed_fee = self.get_required_fee(operation_method, self.__database_api_identifier)[0]["amount"]
        start_fee_pool_balance = needed_fee * 2
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, start_fee_pool_balance,
                                                        self.__database_api_identifier)
        lcc.log_info("Added '{}' assets value to '{}' contract fee pool successfully".format(start_fee_pool_balance,
                                                                                             contract_id))

        lcc.set_step("Get a contract's fee pool balance and store")
        fee_pool_balance = self.get_contract_pool_balance(contract_id)
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'. "
                     "Fee pool balance: '{}' assets".format(contract_id, fee_pool_balance))

        lcc.set_step("Add two accounts to whitelist (not fee pool sender)")
        whitelist = [self.echo_acc5, self.echo_acc6]
        for account in whitelist:
            full_whitelist.append(account)
            full_whitelist = sorted(full_whitelist, key=self.get_value_for_sorting_func)
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier, add_to_whitelist=whitelist)
        lcc.log_info("Added '{}' accounts to '{}' contract whitelist successfully".format(full_whitelist, contract_id))

        lcc.set_step("Get a contract's fee pool whitelist and check added accounts")
        contract_pool_whitelist = self.get_contract_pool_whitelist(contract_id)
        require_that("'contract_pool_whitelist'", contract_pool_whitelist["whitelist"], is_list(full_whitelist))

        lcc.set_step("First: call 'greet' method using fee pool sender")
        account_balance = self.utils.get_account_balances(self, self.echo_acc0, self.__database_api_identifier)[
            "amount"]
        collected_operation = self.collect_operations(operation_method, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("'{}' fee pool sender call '{}' contract successfully".format(self.echo_acc0, contract_id))
        account_balance_after_call = self.utils.get_account_balances(self, self.echo_acc0,
                                                                     self.__database_api_identifier)["amount"]
        check_that("'account balance'", int(account_balance_after_call), equal_to(int(account_balance) - needed_fee))

        lcc.set_step("Get a contract's fee pool balance after first call contract by fee pool sender")
        updated_fee_pool_balance = self.get_contract_pool_balance(contract_id)
        check_that("'updated_fee_pool_balance'", updated_fee_pool_balance, equal_to(fee_pool_balance))

        lcc.set_step("Add fee pool sender to whitelist")
        whitelist = [self.echo_acc0]
        for account in whitelist:
            full_whitelist.append(account)
            full_whitelist = sorted(full_whitelist, key=self.get_value_for_sorting_func)
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier, add_to_whitelist=whitelist)
        lcc.log_info("Added '{}' account to '{}' contract whitelist successfully".format(self.echo_acc0, contract_id))

        lcc.set_step("Get a contract's fee pool whitelist and check added account")
        contract_pool_whitelist = self.get_contract_pool_whitelist(contract_id)
        require_that("'contract_pool_whitelist'", contract_pool_whitelist["whitelist"], is_list(full_whitelist))

        lcc.set_step("Second: call 'greet' method using fee pool sender")
        collected_operation = self.collect_operations(operation_method, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("'{}' fee pool sender call '{}' contract successfully".format(self.echo_acc0, contract_id))

        lcc.set_step("Get a contract's fee pool balance after second call contract by fee pool sender")
        updated_fee_pool_balance = self.get_contract_pool_balance(contract_id)
        check_that("'updated_fee_pool_balance'", updated_fee_pool_balance, equal_to(fee_pool_balance - needed_fee))

        lcc.set_step("Remove all accounts from whitelist")
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier,
                                                        remove_from_whitelist=full_whitelist)
        lcc.log_info("All accounts successfully removed from whitelist")

        lcc.set_step("Get a contract's fee pool whitelist and check that whitelist is empty")
        contract_pool_whitelist = self.get_contract_pool_whitelist(contract_id)
        require_that("'contract_pool_whitelist'", contract_pool_whitelist["whitelist"], is_list([]))

        lcc.set_step("Third: call 'greet' method using account that removed from whitelist (not fee pool sender)")
        operation_method = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc5,
                                                                     bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation_method, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("'{}' account call '{}' contract successfully".format(self.echo_acc5, contract_id))

        lcc.set_step(
            "Get a contract's fee pool balance after third call contract by account that removed from whitelist")
        updated_fee_pool_balance = self.get_contract_pool_balance(contract_id)
        check_that("'updated_fee_pool_balance'", updated_fee_pool_balance, equal_to(0))

    @lcc.prop("type", "method")
    @lcc.test("Check work of add and remove accounts to/from blacklist")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def add_remove_accounts_to_from_blacklist(self):
        full_blacklist = []

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to perform two calls contract 'greet' method")
        operation_method = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                     bytecode=self.greet, callee=contract_id)
        needed_fee = self.get_required_fee(operation_method, self.__database_api_identifier)[0]["amount"]
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, needed_fee,
                                                        self.__database_api_identifier)
        lcc.log_info("Added '{}' assets value to '{}' contract fee pool successfully".format(needed_fee, contract_id))

        lcc.set_step("Get a contract's fee pool balance and store")
        fee_pool_balance = self.get_contract_pool_balance(contract_id)
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'. "
                     "Fee pool balance: '{}' assets".format(contract_id, fee_pool_balance))

        lcc.set_step("Add two accounts to blacklist (not fee pool sender)")
        blacklist = [self.echo_acc5, self.echo_acc6]
        for account in blacklist:
            full_blacklist.append(account)
            full_blacklist = sorted(full_blacklist, key=self.get_value_for_sorting_func)
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier, add_to_blacklist=blacklist,
                                                        log_broadcast=False)
        lcc.log_info("Added '{}' accounts to '{}' contract blacklist successfully".format(full_blacklist, contract_id))

        lcc.set_step("Get a contract's fee pool whitelist and check added accounts")
        contract_pool_whitelist = self.get_contract_pool_whitelist(contract_id)
        require_that("'contract_pool_blacklist'", contract_pool_whitelist["blacklist"], is_list(full_blacklist))

        lcc.set_step("First: call 'greet' method using accounts in blacklist")
        for account in blacklist:
            operation_method = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=account,
                                                                         bytecode=self.greet, callee=contract_id)
            collected_operation = self.collect_operations(operation_method, self.__database_api_identifier)
            try:
                self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
                lcc.log_error(
                    "Error: broadcast transaction complete when '{}' don't have enough founds to pay fee".format(
                        account))
            except RPCError as e:
                lcc.log_info(str(e))
        lcc.log_info("'{}' accounts in blacklist can not use '{}' contract fee pool".format(blacklist, contract_id))

        lcc.set_step("Get a contract's fee pool balance after first call contract by fee pool sender")
        updated_fee_pool_balance = self.get_contract_pool_balance(contract_id)
        check_that("'updated_fee_pool_balance'", updated_fee_pool_balance, equal_to(fee_pool_balance))

        lcc.set_step("Add fee pool sender to blacklist")
        blacklist = [self.echo_acc0]
        for account in blacklist:
            full_blacklist.append(account)
            full_blacklist = sorted(full_blacklist, key=self.get_value_for_sorting_func)
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier, add_to_blacklist=blacklist)
        lcc.log_info("Added '{}' account to '{}' contract blacklist successfully".format(self.echo_acc0, contract_id))

        lcc.set_step("Get a contract's fee pool whitelist and check added account")
        contract_pool_whitelist = self.get_contract_pool_whitelist(contract_id)
        require_that("'contract_pool_blacklist'", contract_pool_whitelist["blacklist"], is_list(full_blacklist))

        lcc.set_step("Second: call 'greet' method using fee pool sender")
        account_balance = self.utils.get_account_balances(self, self.echo_acc0, self.__database_api_identifier)[
            "amount"]
        operation_method = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                     bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation_method, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("'{}' fee pool sender call '{}' contract successfully".format(self.echo_acc0, contract_id))
        account_balance_after_call = self.utils.get_account_balances(self, self.echo_acc0,
                                                                     self.__database_api_identifier)["amount"]
        check_that("'account balance'", int(account_balance_after_call), equal_to(int(account_balance) - needed_fee))

        lcc.set_step("Get a contract's fee pool balance after second call contract by fee pool sender")
        updated_fee_pool_balance = self.get_contract_pool_balance(contract_id)
        check_that("'updated_fee_pool_balance'", updated_fee_pool_balance, equal_to(fee_pool_balance))

        lcc.set_step("Remove all accounts from blacklist")
        self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                        self.__database_api_identifier,
                                                        remove_from_blacklist=full_blacklist)
        lcc.log_info("All accounts successfully removed from blacklist")

        lcc.set_step("Get a contract's fee pool whitelist and check that blacklist is empty")
        contract_pool_whitelist = self.get_contract_pool_whitelist(contract_id)
        require_that("'contract_pool_blacklist'", contract_pool_whitelist["blacklist"], is_list([]))

        lcc.set_step("Third: call 'greet' method using account that removed from blacklist (not fee pool sender)")
        operation_method = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc5,
                                                                     bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation_method, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation, log_broadcast=False)
        lcc.log_info("'{}' account call '{}' contract successfully".format(self.echo_acc5, contract_id))

        lcc.set_step(
            "Get a contract's fee pool balance after third call contract by account that removed from whitelist")
        updated_fee_pool_balance = self.get_contract_pool_balance(contract_id)
        check_that("'updated_fee_pool_balance'", updated_fee_pool_balance, equal_to(0))


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("asset_api", "get_contract_pool_whitelist")
@lcc.suite("Negative testing of method 'get_contract_pool_whitelist'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.contract = self.get_byte_code("piggy", "code")

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
    @lcc.test("Get whitelist of a contract that does not have a fee pool")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def whitelist_without_fee_pool(self):
        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Get a contract's pool whitelist. Fee pool not created")
        response_id = self.send_request(self.get_request("get_contract_pool_whitelist", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        lcc.log_info("Call method 'get_contract_pool_balance' with param: '{}'".format(contract_id))

        lcc.set_step("Check simple work of method 'get_contract_pool_whitelist'")
        check_that("'get_contract_pool_whitelist' return error message", response, has_entry("error"), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Add account in whitelist and blacklist at the same time")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def account_in_two_lists(self, get_random_integer):
        value_to_pool = get_random_integer
        whitelist, blacklist = [self.echo_acc0], [self.echo_acc0]

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Add one account to whitelist and blacklist at the same time")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier, add_to_whitelist=whitelist,
                                                            add_to_blacklist=blacklist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can add account to whitelist and blacklist at the same time")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not add account to whitelist and blacklist at the same time")

    @lcc.prop("type", "method")
    @lcc.test("Add account in whitelist/blacklist and remove from whitelist/blacklist at the same time")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def add_account_and_remove_in_the_same_time(self, get_random_integer):
        value_to_pool = get_random_integer
        whitelist, blacklist = [self.echo_acc0], [self.echo_acc0]

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Add one account to whitelist and remove at the same time")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier, add_to_whitelist=whitelist,
                                                            remove_from_whitelist=whitelist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can add account to whitelist and remove at the same time")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not add account to whitelist and remove at the same time")

        lcc.set_step("Add one account to blacklist and remove at the same time")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier, add_to_blacklist=blacklist,
                                                            remove_from_blacklist=blacklist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can add account to blacklist and remove at the same time")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not add account to blacklist and remove at the same time")

    @lcc.prop("type", "method")
    @lcc.test("Add account in whitelist/blacklist and remove from whitelist/blacklist twice")
    @lcc.depends_on("DatabaseApi.GetContractPoolWhitelist.GetContractPoolWhitelist.method_main_check")
    def add_account_and_remove_in_the_same_time(self, get_random_integer):
        value_to_pool = get_random_integer
        whitelist, blacklist = [self.echo_acc0, self.echo_acc0], [self.echo_acc0, self.echo_acc0]

        lcc.set_step("Create contract in the Echo network and get its contract id")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier)

        lcc.set_step("Add fee pool to new contract")
        self.utils.perform_contract_fund_pool_operation(self, self.echo_acc0, contract_id, value_to_pool,
                                                        self.__database_api_identifier)
        lcc.log_info("Fee pool added to '{}' contract successfully".format(contract_id))

        lcc.set_step("Add one account to whitelist twice")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier, add_to_whitelist=whitelist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can add account to whitelist twice")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not add account to whitelist twice")

        lcc.set_step("Remove one account from whitelist twice")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier,
                                                            remove_from_whitelist=whitelist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can remove account from whitelist twice")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not remove account from whitelist twice")

        lcc.set_step("Add one account to blacklist twice")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier, add_to_blacklist=blacklist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can add account to blacklist twice")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not add account to blacklist twice")

        lcc.set_step("Remove one account from blacklist twice")
        try:
            self.utils.perform_contract_whitelist_operation(self, self.echo_acc0, contract_id,
                                                            self.__database_api_identifier,
                                                            remove_from_blacklist=blacklist)
            lcc.log_error(
                "Error: broadcast transaction complete. Can remove account from blacklist twice")
        except RPCError as e:
            lcc.log_info(str(e))
        lcc.log_info("Can not remove account from blacklist twice")
