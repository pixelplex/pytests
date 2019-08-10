# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError
from lemoncheesecake.matching import check_that, is_not_none, this_dict, check_that_entry, is_integer, is_str, \
    has_entry, is_, is_dict, require_that_entry

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_required_fees'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_required_fees")
@lcc.suite("Check work of method 'get_required_fees'", rank=1)
class GetRequiredFees(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_required_fees'")
    def method_main_check(self):
        lcc.set_step("Get required fee for default 'transfer_operation'")
        response_id = self.send_request(self.get_request("get_required_fees", [
            [self.echo_ops.get_operation_json("transfer_operation", example=True),
             self.echo_ops.get_operation_json("transfer_operation", example=True)],
            self.echo_asset]), self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Get required fee for two default 'transfer_operation' in one list operations")

        lcc.set_step("Check simple work of method 'get_required_fees'")
        for i in range(len(response["result"])):
            required_fee = response["result"][i]
            with this_dict(required_fee):
                check_that_entry("amount", is_integer())
                check_that_entry("asset_id", is_str(self.echo_asset))


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_required_fees")
@lcc.suite("Positive testing of method 'get_required_fees'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.amount = 1
        self.transfer_operation = None
        self.required_fee = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.valid_contract_id = None

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
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))
        self.transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                       from_account_id=self.echo_acc0,
                                                                       to_account_id=self.echo_acc1,
                                                                       amount=self.amount)
        lcc.log_info("Transfer operation: '{}'".format(str(self.transfer_operation)))
        self.required_fee = self.get_required_fee(self.transfer_operation, self.__database_api_identifier)
        lcc.log_info("Required fee for transfer transaction: '{}'".format(self.required_fee))
        lcc.log_info("Transfer operation: '{}'".format(str(self.transfer_operation)))
        self.valid_contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                            self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Fee equal to get_required_fee in transfer operation")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_equal_to_get_required_fee(self):
        lcc.set_step("Send transfer transaction with a fee equal to the 'get_required_fee'")
        self.add_fee_to_operation(self.transfer_operation, self.__database_api_identifier,
                                  fee_amount=(self.required_fee[0].get("amount")))
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=self.transfer_operation,
                                                   log_broadcast=False)
        check_that(
            "broadcast transaction complete successfully",
            broadcast_result["trx"], is_not_none(), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Fee higher than get_required_fee in transfer operation")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_higher_than_get_required_fee(self):
        lcc.set_step("Send transfer transaction with a higher fee than the 'get_required_fee'")
        self.add_fee_to_operation(self.transfer_operation, self.__database_api_identifier,
                                  fee_amount=(self.required_fee[0].get("amount") + 1))
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=self.transfer_operation,
                                                   log_broadcast=False)
        check_that(
            "broadcast transaction complete successfully",
            broadcast_result["trx"], is_not_none(), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Try to get fee in eETH")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_in_eth_asset(self):
        lcc.set_step("Get in eETH asset")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=self.echo_acc0,
                                                         to_account_id=self.echo_acc1, amount=self.amount,
                                                         fee_asset_id=self.eth_asset)
        params = [[operation], self.eth_asset]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        response = self.get_response(response_id)
        with this_dict(response["result"][0]):
            check_that_entry("amount", is_integer(), quiet=True)
            check_that_entry("asset_id", is_(self.eth_asset), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Required fee to call contract")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_to_call_contract(self):
        lcc.set_step("Get required fee for 'contract_call_operation' with nonexistent method byte code")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet,
                                                              callee=self.valid_contract_id)
        params = [[operation], self.echo_asset]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        result = self.get_response(response_id)["result"][0]
        with this_dict(result):
            require_that_entry("fee", is_dict(), quiet=True)
            with this_dict(result["fee"]):
                check_that_entry("amount", is_integer(), quiet=True)
                check_that_entry("asset_id", is_(self.echo_asset), quiet=True)
            require_that_entry("user_to_pay", is_dict(), quiet=True)
            with this_dict(result["user_to_pay"]):
                check_that_entry("amount", is_integer(), quiet=True)
                check_that_entry("asset_id", is_(self.echo_asset), quiet=True)


@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_required_fees")
@lcc.suite("Negative testing of method 'get_required_fees'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None
        self.amount = 1
        self.transfer_operation_ex = None
        self.transfer_operation = None
        self.contract = self.get_byte_code("piggy", "code")
        self.valid_contract_id = None
        self.nonexistent_asset_id = None

    def get_required_fees(self, operations, asset, negative=False):
        params = [[operations], asset]
        response_id = self.send_request(self.get_request("get_required_fees", params), self.__database_api_identifier)
        return self.get_response(response_id, negative=negative)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.nonexistent_asset_id = self.utils.get_nonexistent_asset_id(self, self.__database_api_identifier)
        lcc.log_info("Nonexistent asset id is '{}'".format(self.nonexistent_asset_id))
        self.echo_acc0 = self.get_account_id(self.accounts[0], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc1 = self.get_account_id(self.accounts[1], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}''".format(self.echo_acc0, self.echo_acc1))
        self.transfer_operation_ex = self.echo_ops.get_operation_json("transfer_operation", example=True)
        lcc.log_info("Transfer operation example: '{}'".format(str(self.transfer_operation_ex)))
        self.transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                       from_account_id=self.echo_acc0,
                                                                       to_account_id=self.echo_acc1,
                                                                       amount=self.amount)
        lcc.log_info("Transfer operation: '{}'".format(str(self.transfer_operation)))
        self.valid_contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                            self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Call method without params and with insufficient number of params")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def call_method_without_params_or_insufficient(self):
        lcc.set_step("Call method without params")
        response_id = self.send_request(self.get_request("get_required_fees"), self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True,
        )

        lcc.set_step("Call method with insufficient number of params")
        response_id = self.send_request(self.get_request("get_required_fees", [[self.transfer_operation_ex]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True,
        )

    @lcc.prop("type", "method")
    @lcc.test("Call method with wrong params")
    @lcc.tags("Bug: 'ECHO-681'")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def call_method_with_wrong_params(self, get_all_random_types):
        random_type_names = list(get_all_random_types.keys())
        random_values = list(get_all_random_types.values())

        lcc.set_step("Call method with wrong params. Wrong param operation")
        for i in range(len(get_all_random_types)):
            # todo: remove if. Bug: "ECHO-681"
            if i == 4:
                continue
            response = self.get_required_fees(random_values[i], self.echo_asset, negative=True)
            check_that(
                "'get_required_fees' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

        lcc.set_step("Call method with wrong params. Wrong param asset")
        for i in range(len(get_all_random_types)):
            response = self.get_required_fees(self.transfer_operation_ex, random_values[i], negative=True)
            check_that(
                "'get_required_fees' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent asset_id")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_asset_id_in_method_call(self):
        lcc.set_step("Get required fee for default 'transfer_operation' but with nonexistent asset_id")
        response = self.get_required_fees(self.transfer_operation_ex, self.nonexistent_asset_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True,
        )

    @lcc.prop("type", "method")
    @lcc.test("Fee lower than get_required_fee in transfer operation")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_lower_than_get_required_fee(self):
        lcc.set_step("Send transfer transaction with a lower fee than the 'get_required_fee'")
        required_fee = self.get_required_fee(self.transfer_operation, self.__database_api_identifier)
        self.add_fee_to_operation(self.transfer_operation, self.__database_api_identifier,
                                  fee_amount=(required_fee[0].get("amount") - 1))
        try:
            self.echo_ops.broadcast(echo=self.echo, list_operations=self.transfer_operation)
            lcc.log_error("Error: broadcast transaction complete with insufficient.")
        except RPCError as e:
            lcc.log_info(str(e))

    @lcc.prop("type", "method")
    @lcc.test("Sender don't have enough fee")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def sender_do_not_have_enough_fee(self, get_random_valid_account_name):
        lcc.set_step("Get account id")
        account_name = get_random_valid_account_name
        account_id = self.get_account_id(account_name, self.__database_api_identifier,
                                         self.__registration_api_identifier)
        lcc.log_info("New account created, account_id='{}'".format(account_id))

        lcc.set_step("Get account balance")

        params = [account_id, [self.echo_asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        all_balance_amount = response.get("result")[0].get("amount")
        lcc.log_info(
            "Account '{}' has '{}' in '{}' asset".format(account_id, all_balance_amount, self.echo_asset))

        lcc.set_step("Send transfer transaction with a fee equal to the 'get_required_fee', "
                     "but sender don't have enough fee")
        operation = self.echo_ops.get_transfer_operation(echo=self.echo, from_account_id=account_id,
                                                         to_account_id=self.echo_acc1, amount=self.amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        try:
            self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            lcc.log_error("Error: broadcast transaction complete with insufficient.")
        except RPCError as e:
            lcc.log_info(str(e))

    @lcc.prop("type", "method")
    @lcc.test("Nonexistent contract byte code")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_contract_byte_code(self):
        not_valid_contract = "6e5964425a64326457664a44516474594a615878"

        lcc.set_step("Get required fee for 'contract_create_operation' with nonexistent byte code")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=not_valid_contract)
        response = self.get_required_fees(operation, self.echo_asset, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Nonexistent asset id")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_asset_id_in_operation(self):
        lcc.set_step("Get required fee for 'contract_create_operation' with nonexistent asset in operation")
        operation = self.echo_ops.get_contract_create_operation(echo=self.echo, registrar=self.echo_acc0,
                                                                bytecode=self.contract, value_amount=self.amount,
                                                                value_asset_id=self.nonexistent_asset_id)
        response = self.get_required_fees(operation, self.echo_asset, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Nonexistent method byte code")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_method_byte_code(self, get_random_hex_string):
        lcc.set_step("Get required fee for 'contract_call_operation' with nonexistent method byte code")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=get_random_hex_string,
                                                              callee=self.valid_contract_id)
        response = self.get_required_fees(operation, self.echo_asset, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )
