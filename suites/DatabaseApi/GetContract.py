# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, check_that, require_that, ends_with, is_, is_list, \
    equal_to, not_equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_contract'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_contract")
@lcc.suite("Check work of method 'get_contract'", rank=1)
class GetContract(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.contract_id = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
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


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_contract")
@lcc.suite("Positive testing of method 'get_contract'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract_piggy = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")
        self.breakPiggy = self.get_byte_code("piggy", "breakPiggy")

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}'".format(self.__database_api_identifier,
                                                                           self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
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
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                 self.__database_api_identifier)

        lcc.set_step("Get the contract by id")
        response_id = self.send_request(self.get_request("get_contract", [contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(contract_id))

        lcc.set_step("Check response of 'get_contract' before call any method. Store contract storage")
        contract_info = response["result"][1]
        code_before_contract_call = contract_info["code"]
        check_that("'contract code'", self.contract_piggy, ends_with(code_before_contract_call), quiet=True)
        storage_before_contract_call = contract_info["storage"]
        lcc.log_info("Store contract storage before call 'greet' method")

        lcc.set_step("Call contract method that nothing do with contract fields")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
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
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
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
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
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
