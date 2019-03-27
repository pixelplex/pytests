# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from echopy.echoapi.ws.exceptions import RPCError
from lemoncheesecake.matching import check_that, is_not_none, this_dict, check_that_entry, is_integer, is_str, \
    has_entry

from common.base_test import BaseTest
from common.echo_operation import EchoOperations

SUITE = {
    "description": "Method 'get_required_fee'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("get_required_fees")
@lcc.suite("Check work of method 'get_required_fees'", rank=1)
class GetRequiredFees(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.echo_operations = EchoOperations()
        self.asset = "1.3.0"

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_required_fees'")
    def method_main_check(self):
        lcc.set_step("Get required fee for default 'transfer_operation'")
        response_id = self.send_request(self.get_request("get_required_fees", [
            [self.echo_operations.get_operation_json("transfer_operation", example=True),
             self.echo_operations.get_operation_json("transfer_operation", example=True)], self.asset]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check simple work of method 'get_required_fees'")
        for i in range(len(response["result"])):
            required_fee = response["result"][i]
            with this_dict(required_fee):
                check_that_entry("amount", is_integer())
                check_that_entry("asset_id", is_str(self.asset))


@lcc.prop("testing", "positive")
@lcc.tags("get_required_fees")
@lcc.suite("Positive testing of method 'get_required_fees'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.echo_operations = EchoOperations()
        self.amount = 1
        self.asset = "1.3.0"
        self.account_1 = "test-echo-1"
        self.account_2 = "test-echo-2"
        self.operation = None
        self.required_fee = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.account_1 = self.get_account_id(self.account_1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.account_2 = self.get_account_id(self.account_2, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.account_1,
                                                                     to_account_id=self.account_2, amount=self.amount)
        self.required_fee = self.get_required_fee(self.operation, self.__database_api_identifier)
        lcc.log_info("Required fee for transfer transaction: '{}'".format(self.required_fee))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Fee equal to get_required_fee in transfer operation")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_equal_to_get_required_fee(self):
        lcc.set_step("Send transfer transaction with a fee equal to the 'get_required_fee'")
        self.add_fee_to_operation(self.operation, self.__database_api_identifier,
                                  fee_amount=(self.required_fee[0].get("amount")))
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=self.operation,
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
        self.add_fee_to_operation(self.operation, self.__database_api_identifier,
                                  fee_amount=(self.required_fee[0].get("amount") + 1))
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=self.operation,
                                                          log_broadcast=False)
        check_that(
            "broadcast transaction complete successfully",
            broadcast_result["trx"], is_not_none(), quiet=True
        )


@lcc.prop("testing", "negative")
@lcc.tags("get_required_fees")
@lcc.suite("Negative testing of method 'get_required_fees'", rank=3)
class NegativeTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.echo_operations = EchoOperations()
        self.amount = 1
        self.asset = "1.3.0"
        self.account_1 = "test-echo-1"
        self.account_2 = "test-echo-2"
        self.new_account = "empty-account"
        self.operation = None
        self.contract = self.get_byte_code("piggy_code")
        self.valid_contract_id = None
        self.list_asset_ids = []
        self.nonexistent_asset_id = None
        self.required_fee = None

    def get_nonexistent_asset_id(self, symbol=""):
        response_id = self.send_request(self.get_request("list_assets", [symbol, 100]), self.__database_api_identifier)
        response = self.get_response(response_id)
        for i in range(len(response["result"])):
            self.list_asset_ids.append(response["result"][i]["id"])
        if len(response["result"]) == 100:
            return self.get_nonexistent_asset_id(symbol=response["result"][-1]["symbol"])
        sorted_list_asset_ids = sorted(self.list_asset_ids, key=self.get_value_for_sorting_func)
        return "1.3.{}".format(str(int(sorted_list_asset_ids[-1][4:]) + 1))

    def get_valid_contract_id(self, registrar, contract):
        operation = self.echo_operations.get_create_contract_operation(echo=self.echo, registrar=registrar,
                                                                       bytecode=contract, fee_amount=500)
        broadcast_result = self.echo_operations.broadcast(echo=self.echo, list_operations=operation,
                                                          log_broadcast=False)
        contract_result = self.get_operation_results_ids(broadcast_result)
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        self.__database_api_identifier)
        contract_id_16 = self.get_trx_completed_response(response_id)
        return self.get_contract_id(contract_id_16)

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.nonexistent_asset_id = self.get_nonexistent_asset_id()
        lcc.log_info("Nonexistent asset id: '{}'".format(self.nonexistent_asset_id))
        self.account_1 = self.get_account_id(self.account_1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.account_2 = self.get_account_id(self.account_2, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.new_account = self.get_account_id(self.new_account, self.__database_api_identifier,
                                               self.__registration_api_identifier)
        self.operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.account_1,
                                                                     to_account_id=self.account_2, amount=self.amount)
        self.required_fee = self.get_required_fee(self.operation, self.__database_api_identifier)
        self.valid_contract_id = self.get_valid_contract_id(self.account_1, self.contract)
        lcc.log_info("Valid contract id: '{}'".format(self.valid_contract_id))

    def teardown_suite(self):
        lcc.set_step("Teardown suite for {}".format(self.__class__.__name__))
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
        response_id = self.send_request(self.get_request("get_required_fees", [
            [self.echo_operations.get_operation_json("transfer_operation", example=True)]]),
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
            response_id = self.send_request(
                self.get_request("get_required_fees", [[random_values[i]], self.asset]),
                self.__database_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_required_fees' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

        lcc.set_step("Call method with wrong params. Wrong param asset")
        for i in range(len(get_all_random_types)):
            response_id = self.send_request(self.get_request("get_required_fees", [
                [self.echo_operations.get_operation_json("transfer_operation", example=True)],
                random_values[i]]), self.__database_api_identifier)
            response = self.get_response(response_id, negative=True)
            check_that(
                "'get_required_fees' return error message with '{}' params".format(random_type_names[i]),
                response, has_entry("error"), quiet=True,
            )

    @lcc.prop("type", "method")
    @lcc.test("Use in method call nonexistent asset_id")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_asset_id_in_method_call(self):
        lcc.set_step("Get required fee for default 'transfer_operation' but with nonexistent asset_id")
        response_id = self.send_request(self.get_request("get_required_fees", [
            [self.echo_operations.get_operation_json("transfer_operation", example=True)], self.nonexistent_asset_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True,
        )

    @lcc.prop("type", "method")
    @lcc.test("Fee lower than get_required_fee in transfer operation")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_lower_than_get_required_fee(self):
        lcc.set_step("Send transfer transaction with a lower fee than the 'get_required_fee'")
        self.add_fee_to_operation(self.operation, self.__database_api_identifier,
                                  fee_amount=(self.required_fee[0].get("amount") - 1))
        try:
            self.echo_operations.broadcast(echo=self.echo, list_operations=self.operation)
            lcc.log_error("Error: broadcast transaction complete with insufficient.")
        except RPCError as e:
            lcc.log_info(str(e))

    @lcc.prop("type", "method")
    @lcc.test("Sender don't have enough fee")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def sender_do_not_have_enough_fee(self):
        lcc.set_step("Get account balance")
        params = [self.new_account, [self.asset]]
        response_id = self.send_request(self.get_request("get_account_balances", params),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        all_balance_amount = response.get("result")[0].get("amount")
        lcc.log_info("Account '{}' has '{}' in '{}' asset".format(self.new_account, all_balance_amount, self.asset))

        lcc.set_step("Send all assets to any account, if account balance is not 0")
        if all_balance_amount != 0:
            operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.new_account,
                                                                    to_account_id=self.account_2,
                                                                    amount=all_balance_amount)
            required_fee = self.get_required_fee(operation, self.__database_api_identifier)
            required_fee = required_fee[0].get("amount")
            operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.new_account,
                                                                    to_account_id=self.account_2,
                                                                    amount=all_balance_amount - required_fee)
            collected_operation = self.collect_operations(operation, self.__database_api_identifier)
            self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Send transfer transaction with a fee equal to the 'get_required_fee', "
                     "but sender don't have enough fee")
        operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.new_account,
                                                                to_account_id=self.account_2, amount=self.amount)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        try:
            self.echo_operations.broadcast(echo=self.echo, list_operations=collected_operation)
            lcc.log_error("Error: broadcast transaction complete with insufficient.")
        except RPCError as e:
            lcc.log_info(str(e))

    @lcc.prop("type", "method")
    # todo: add test. Bug: "ECHO-666"
    @lcc.tags("Bug: 'ECHO-666'")
    @lcc.disabled()
    @lcc.test("Try to get fee in eETH")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def fee_in_eth_asset(self):
        lcc.set_step("Get in eETH asset")
        eth_asset_id = "1.3.48"
        operation = self.echo_operations.get_transfer_operation(echo=self.echo, from_account_id=self.account_1,
                                                                to_account_id=self.account_2, amount=self.amount,
                                                                fee_asset_id=eth_asset_id)
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], eth_asset_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.tags("Bug: 'ECHO-653'")
    @lcc.test("Nonexistent contract byte code")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_contract_byte_code(self):
        # todo change on get_random_hex_string. Bug: "ECHO-653"
        not_valid_contract = "6e5964425a64326457664a44516474594a615878"

        lcc.set_step("Get required fee for 'create_contract_operation' with nonexistent byte code")
        operation = self.echo_operations.get_create_contract_operation(echo=self.echo, registrar=self.account_1,
                                                                       bytecode=not_valid_contract)
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], self.asset]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Nonexistent asset id")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_asset_id_in_operation(self):
        lcc.set_step("Get required fee for 'create_contract_operation' with nonexistent asset in operation")
        operation = self.echo_operations.get_create_contract_operation(echo=self.echo, registrar=self.account_1,
                                                                       bytecode=self.contract, value_amount=self.amount,
                                                                       value_asset_id=self.nonexistent_asset_id)
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], self.asset]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )

    @lcc.prop("type", "method")
    @lcc.test("Nonexistent method byte code")
    @lcc.depends_on("DatabaseApi.GetRequiredFees.GetRequiredFees.method_main_check")
    def nonexistent_method_byte_code(self, get_random_hex_string):
        lcc.set_step("Get required fee for 'call_contract_operation' with nonexistent method byte code")
        operation = self.echo_operations.get_call_contract_operation(echo=self.echo, registrar=self.account_1,
                                                                     bytecode=get_random_hex_string,
                                                                     callee=self.get_valid_contract_id(self.account_1,
                                                                                                       self.contract))
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], self.asset]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, negative=True)
        check_that(
            "'get_required_fees' return error message",
            response, has_entry("error"), quiet=True
        )
