# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, check_that, require_that, ends_with, is_, is_list, \
    equal_to, not_equal_to, has_length

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract'"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.prop("suite_run_option_2", "positive")
@lcc.prop("suite_run_option_3", "negative")
@lcc.tags("database_api", "get_contract")
@lcc.suite("Check work of method 'get_contract'", rank=1)
class GetContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.contract_id = None
        self.echo_acc0 = None

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
        self.contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract,
                                                      self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_contract'")
    def method_main_check(self):
        lcc.set_step("Get the contract by id")
        response_id = self.send_request(self.get_request("get_contract", [self.contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(self.contract_id))

        lcc.set_step("Check simple work of method 'get_contract'")
        contract_type = response["result"][0]
        require_that("contract index", contract_type, is_(0))
        contract_info = response["result"][1]
        if not self.validator.is_hex(contract_info["code"]):
            lcc.log_error("Wrong format of 'code', got: {}".format(contract_info["code"]))
        else:
            lcc.log_info("'code' has correct format: hex")

        contract_storage = contract_info["storage"]
        if not self.validator.is_hex(contract_storage[0][0]):
            lcc.log_error("Wrong format of 'contract storage var 1', got: {}".format(contract_storage[0][0]))
        else:
            lcc.log_info("'contract storage var 1' has correct format: hex")
        check_that("'contract storage var 2'", contract_storage[0][1], is_list(), quiet=True)


@lcc.prop("suite_run_option_2", "positive")
@lcc.tags("database_api", "get_contract")
@lcc.suite("Positive testing of method 'get_contract'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet()")
        self.breakPiggy = self.get_byte_code("piggy", "breakPiggy()")
        self.dynamic_fields_contract = self.get_byte_code("dynamic_fields", "code")
        self.set_uint = self.get_byte_code("dynamic_fields", "onUint256Changed(uint256)")
        self.get_uint = self.get_byte_code("dynamic_fields", "getUint256()")
        self.delete_uint = self.get_byte_code("dynamic_fields", "deleteUint256()")
        self.set_string = self.get_byte_code("dynamic_fields", "onStringChanged(string)")
        self.get_string = self.get_byte_code("dynamic_fields", "getString()")
        self.delete_string = self.get_byte_code("dynamic_fields", "deleteString()")

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
    @lcc.test("Check contract info using method 'get_contract'")
    @lcc.depends_on("DatabaseApi.GetContract.GetContract.method_main_check")
    def check_contract_info_after_calling_contract_method(self):
        lcc.set_step("Create 'piggy' contract in ECHO network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Get the contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(contract_id))

        lcc.set_step("Check response of 'get_contract' before call any method. Store contract storage")
        contract_info = response["result"][1]
        code_before_contract_call = contract_info["code"]
        check_that("'contract code'", self.piggy_contract, ends_with(code_before_contract_call), quiet=True)
        storage_before_contract_call = contract_info["storage"]
        lcc.log_info("Store contract storage before call 'greet' method")

        lcc.set_step("Call contract method that nothing do with contract fields")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get response of 'get_contract' after contract call")
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        contract_info = response["result"][1]
        code_after_contract_call = contract_info["code"]
        storage_after_contract_call = contract_info["storage"]
        lcc.log_info("Store contract storage after call 'greet' method")

        lcc.set_step("Check contract info before and after call 'greet' method")
        check_that("'code after contract call'", code_after_contract_call, equal_to(code_before_contract_call),
                   quiet=True)
        check_that("'storage after contract call'", storage_before_contract_call, equal_to(storage_after_contract_call),
                   quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check contract info after contract destroy")
    @lcc.depends_on("DatabaseApi.GetContract.GetContract.method_main_check")
    def check_contract_destroy_method(self):
        lcc.set_step("Create 'piggy' contract in ECHO network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Get the contract by id and store info before destroy contract")
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        contract_info = response["result"][1]
        contract_code = contract_info["code"]
        contract_storage = contract_info["storage"]
        lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(contract_id))

        lcc.set_step("Call method 'breakPiggy' to destroy contract")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.breakPiggy, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get response of 'get_contract' after call method that destroy contract")
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(contract_id))

        lcc.set_step("Check contract info after contract destroy")
        contract_info = response["result"][1]
        with this_dict(contract_info):
            check_that_entry("code", not_equal_to(contract_code), quiet=True)
            check_that_entry("code", equal_to(""), quiet=True)
            check_that_entry("storage", not_equal_to(contract_storage), quiet=True)
            check_that_entry("storage", equal_to([]), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Verification of changes in case of dynamic fields of a contract")
    @lcc.depends_on("DatabaseApi.GetContract.GetContract.method_main_check")
    def check_storage_field_in_contract_info(self, get_random_integer, get_random_string):
        int_param = get_random_integer
        string_param = get_random_string

        lcc.set_step("Create 'dynamic_fields' contract in ECHO network")
        contract_dynamic_fields_id = self.utils.get_contract_id(self, self.echo_acc0, self.dynamic_fields_contract,
                                                                self.__database_api_identifier)

        lcc.set_step("Get contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_dynamic_fields_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with param: '{}'".format(contract_dynamic_fields_id))

        lcc.set_step("Check storage of created contract without any fields")
        contract_storage = response["result"][1]["storage"]
        check_that("'contract storage'", contract_storage, is_list([]), quiet=True)

        lcc.set_step("Call method 'set_uint' to add uint field in contract")
        bytecode = self.set_uint + self.get_byte_code_param(int_param, param_type=int)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Check that uint field created in contract. Call method 'get_uint'")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_uint,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=int)
        check_that("'uint field in contract'", contract_output, equal_to(int_param))

        lcc.set_step("Get contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_dynamic_fields_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with param: '{}'".format(contract_dynamic_fields_id))

        lcc.set_step("Check storage of created contract with uint field")
        contract_storage_with_int = response["result"][1]["storage"]
        require_that("'contract storage'", contract_storage_with_int, has_length(1))

        require_that("'contract storage'", contract_storage_with_int, not_equal_to([]), quiet=True, )
        if not self.validator.is_hex(contract_storage_with_int[0][0]):
            lcc.log_error("Wrong format of 'contract storage var 1', got: {}".format(contract_storage_with_int[0][0]))
        else:
            lcc.log_info("'contract storage var 1' has correct format: hex")
        check_that("'contract storage var 2'", contract_storage_with_int[0][1], is_list(), quiet=True)

        lcc.set_step("Call method 'set_string' to add string field in contract")
        bytecode = self.set_string + self.get_byte_code_param(string_param, param_type=str)
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=bytecode,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Check that string field created in contract. Call method 'get_string'")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_string,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        contract_output = self.get_contract_output(contract_result, output_type=str,
                                                   len_output_string=len(string_param))
        check_that("'string field in contract'", contract_output, equal_to(string_param))

        lcc.set_step("Get contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_dynamic_fields_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with param: '{}'".format(contract_dynamic_fields_id))

        lcc.set_step("Check storage of created contract with string field")
        contract_storage_with_string = response["result"][1]["storage"]
        require_that("'contract storage'", contract_storage_with_string, has_length(3))
        check_that("'contract storage'", contract_storage_with_string[0], equal_to(contract_storage_with_int[0]))
        for i in range(len(contract_storage_with_string)):
            if not self.validator.is_hex(contract_storage_with_string[i][0]):
                lcc.log_error(
                    "Wrong format of 'contract storage var 1', got: {}".format(contract_storage_with_string[0][0]))
            else:
                lcc.log_info("'contract storage var 1' has correct format: hex")
            check_that("'contract storage var 2'", contract_storage_with_string[i][1], is_list(), quiet=True)

        lcc.set_step("Call method 'delete_string' to delete string field in contract")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.delete_string,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_dynamic_fields_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with param: '{}'".format(contract_dynamic_fields_id))

        lcc.set_step("Check storage of contract after delete string field")
        contract_storage = response["result"][1]["storage"]
        require_that("'contract storage'", contract_storage, has_length(1))
        require_that("'contract storage'", contract_storage, equal_to(contract_storage_with_int))

        lcc.set_step("Call method 'delete_uint' to delete uint field in contract")
        operation = self.echo_ops.get_contract_call_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.delete_uint,
                                                              callee=contract_dynamic_fields_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_dynamic_fields_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with param: '{}'".format(contract_dynamic_fields_id))

        lcc.set_step("Check storage of contract after delete uint field. All fields deleted")
        contract_storage = response["result"][1]["storage"]
        check_that("'contract storage'", contract_storage, is_list([]), quiet=True)
