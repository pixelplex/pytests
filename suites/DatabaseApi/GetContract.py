# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import this_dict, check_that_entry, check_that, \
    require_that, ends_with, is_, is_list, equal_to

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
        self.contract_greet = self.get_byte_code("piggy", "greet")
        self.contract_breakPiggy = self.get_byte_code("piggy", "breakPiggy")

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
        self.contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract_piggy,
                                                      self.__database_api_identifier)

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Create contract and check get_contract method with piggy contract")
    @lcc.depends_on("DatabaseApi.GetContract.GetContract.method_main_check")
    def check_contract_changes_after_calling_greet_method(self):
        lcc.set_step("Get the contract by id")
        response_id = self.send_request(self.get_request("get_contract", [self.contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_contract' with contract_id='{}' parameter".format(self.contract_id))

        lcc.set_step("Get response of 'get_contract'")
        contract_before_calling = response["result"][1]
        check_that("'contract code'", self.contract_piggy, ends_with(contract_before_calling["code"]), quiet=True)
        store_storage = contract_before_calling["storage"]
        lcc.log_info("Store contract before calling")

        lcc.set_step("Сall the greet contract method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo,
                                                              registrar=self.echo_acc0,
                                                              bytecode=self.contract_greet,
                                                              callee=self.contract_id)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get response of 'get_contract' after calling")
        response_id = self.send_request(self.get_request("get_contract", [self.contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        contract = response["result"][1]

        lcc.set_step("Check response changes")
        check_that("'response'", contract_before_calling, equal_to(contract), quiet=True)
        check_that("'compare storage'", store_storage, equal_to(contract["storage"]), quiet=True)

    @lcc.prop("type", "method")
    @lcc.test("Check destroy contract method")
    @lcc.depends_on("DatabaseApi.GetContract.GetContract.method_main_check")
    def check_destroy_contract_method(self):
        lcc.set_step("Check method contract destruction")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo,
                                                              registrar=self.echo_acc0,
                                                              bytecode=self.contract_breakPiggy,
                                                              callee=self.contract_id)

        collected_operation = self.collect_operations(operation, self.__database_api_identifier)

        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get response of 'get_contract' after calling destroy contract method")
        response_id = self.send_request(self.get_request("get_contract", [self.contract_id]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        contract = response["result"][1]
        lcc.log_info("contract response {}".format(contract))
        with this_dict(contract):
            check_that_entry("code", equal_to(""), quiet=True)
            check_that_entry("storage", equal_to([]), quiet=True)
