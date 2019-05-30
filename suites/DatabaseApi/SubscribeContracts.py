# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_none, this_dict, has_length, check_that_entry, is_integer, is_, \
    equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'subscribe_contracts'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "subscribe_contracts")
@lcc.suite("Check work of method 'subscribe_contracts'", rank=1)
class SubscribeContracts(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

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
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'subscribe_contracts'")
    def method_main_check(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.contract, self.__database_api_identifier,
                                                 value_amount=10)

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        lcc.set_step("Check subscribe contracts")
        check_that(
            "'subscribe contracts'",
            response["result"],
            is_none(),
        )

        lcc.set_step("Call 'greet' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, object_id=self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_HISTORY))

        lcc.set_step("Check notice 'subscribe_contracts'")
        with this_dict(notice):
            if check_that("global_properties", notice, has_length(5)):
                if not self.validator.is_contract_history_id(notice["id"]):
                    lcc.log_error("Wrong format of 'id', got: {}".format(notice["id"]))
                else:
                    lcc.log_info("'id' has correct format: contract_history_object_type")
                if not self.validator.is_contract_id(notice["contract"]):
                    lcc.log_error("Wrong format of 'contract', got: {}".format(notice["contract"]))
                else:
                    lcc.log_info("'contract' has correct format: contract_id")
                if not self.validator.is_operation_history_id(notice["operation_id"]):
                    lcc.log_error("Wrong format of 'operation_id', got: {}".format(notice["operation_id"]))
                else:
                    lcc.log_info("'operation_id' has correct format: operation_history_id")
                check_that_entry("sequence", is_integer(), quiet=True)
                if not self.validator.is_contract_history_id(notice["next"]):
                    lcc.log_error("Wrong format of 'next', got: {}".format(notice["next"]))
                else:
                    lcc.log_info("'next' has correct format: contract_history_object_type")
                check_that_entry("next", is_("2.16.{}".format(str((int(notice["id"].split('.')[2]) - 1)))))


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "subscribe_contracts")
@lcc.suite("Positive testing of method 'subscribe_contracts'", rank=2)
class PositiveTesting(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.__history_api_identifier = None
        self.piggy_contract = self.get_byte_code("piggy", "code")
        self.greet = self.get_byte_code("piggy", "greet")
        self.get_pennie = self.get_byte_code("piggy", "getPennie")
        self.break_piggy = self.get_byte_code("piggy", "breakPiggy")
        self.create_contract = self.get_byte_code("contract_create_contract", "code")
        self.deploy_contract = self.get_byte_code("contract_create_contract", "deploy_contract")
        self.get_creator = self.get_byte_code("contract_create_contract", "created_contract")["get_creator"]
        self.tr_asset_to_creator = self.get_byte_code("contract_create_contract", "created_contract")[
            "tr_asset_to_creator"]

    def set_subscribe_callback(self, callback, notify_remove_create=False):
        params = [callback, notify_remove_create]
        response_id = self.send_request(self.get_request("set_subscribe_callback", params),
                                        self.__database_api_identifier)
        result = self.get_response(response_id)["result"]
        if result is not None:
            raise Exception("Subscription not issued")
        lcc.log_info("Call method 'set_subscribe_callback', 'notify_remove_create'={}".format(notify_remove_create))

    def get_contract_history(self, contract_id, stop="1.10.0", start="1.10.0", limit=1, log_response=False):
        params = [contract_id, stop, limit, start]
        response_id = self.send_request(self.get_request("get_contract_history", params), self.__history_api_identifier)
        response = self.get_response(response_id, log_response=log_response)
        lcc.log_info("Call method 'get_contract_history' with: contract_id='{}', stop='{}', limit='{}', start='{}' "
                     "parameters".format(contract_id, stop, limit, start))
        return response

    @staticmethod
    def check_operations_ids_in_notice(response, notice, contract_id):
        counter = 0
        for i in range(len(response)):
            operation_history_id = response[i]["id"]
            for j in range(len(response)):
                notice_id = notice[j]["id"]
                notice_contract_id = notice[j]["contract"]
                notice_operation_history_id = notice[j]["operation_id"]
                if notice_operation_history_id != operation_history_id:
                    if counter != len(response):
                        counter += 1
                        continue
                    lcc.log_error("No '{}' operation in the notice".format(operation_history_id))
                if notice_contract_id != contract_id:
                    lcc.log_error("Notice has incorrect contract id, got '{}', but need '{}'".format(notice_contract_id,
                                                                                                     contract_id))
                lcc.log_info("Received and check notice with id '{}'".format(notice_id))
                lcc.log_info("Notice has correct contract id: '{}'".format(notice_contract_id))
                lcc.log_info("Operations are the same: notice has operation '{}' like contract history='{}'".format(
                    notice_operation_history_id, operation_history_id))
                break

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        self.__history_api_identifier = self.get_identifier("history")
        lcc.log_info(
            "API identifiers are: database='{}', registration='{}', "
            "history='{}'".format(self.__database_api_identifier, self.__registration_api_identifier,
                                  self.__history_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo account is '{}'".format(self.echo_acc0))
        self.utils.cancel_all_subscriptions(self, self.__database_api_identifier)
        lcc.log_info("Canceled all subscriptions successfully")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Check notices of contract")
    @lcc.depends_on("DatabaseApi.SubscribeContracts.SubscribeContracts.method_main_check")
    def check_different_types_of_contract_notices(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'Piggy' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.piggy_contract,
                                                 self.__database_api_identifier, value_amount=10)

        lcc.set_step("Subscribe created contract")
        response_id = self.send_request(self.get_request("subscribe_contracts", [[contract_id]]),
                                        self.__database_api_identifier)
        self.get_response(response_id)

        lcc.set_step("Call 'greet' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.greet, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, object_id=self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_HISTORY))

        lcc.set_step("Get contract history")
        operation_history_id = self.get_contract_history(contract_id)["result"][0]["id"]

        lcc.set_step("Check notice about updated contract history")
        with this_dict(notice):
            check_that_entry("contract", equal_to(contract_id))
            check_that_entry("operation_id", equal_to(operation_history_id))

        lcc.set_step("Call 'getPennie' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_pennie, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        # todo: add info balance_obj. Improve: ECHO-815
        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, notices_list=True)

        lcc.set_step("Get contract history")
        response = self.get_contract_history(contract_id, limit=2)["result"]

        lcc.set_step("Check notice about updated contract history")
        self.check_operations_ids_in_notice(response, notice, contract_id)

        lcc.set_step("Call 'breakPiggy' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.break_piggy, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of created contract")
        notice = self.get_notice(subscription_callback_id, notices_list=True)

        lcc.set_step("Get contract history")
        response = self.get_contract_history(contract_id, limit=2)["result"]

        lcc.set_step("Check notice about updated contract history")
        self.check_operations_ids_in_notice(response, notice, contract_id)

    @lcc.prop("type", "method")
    @lcc.test("Check notices of contract created by another contract")
    @lcc.depends_on("DatabaseApi.SubscribeContracts.SubscribeContracts.method_main_check")
    def check_notices_of_contract_created_by_another_contract(self, get_random_integer):
        lcc.set_step("Set subscribe callback")
        subscription_callback_id = get_random_integer
        self.set_subscribe_callback(subscription_callback_id)

        lcc.set_step("Create 'contract_create_contract' contract in the Echo network")
        contract_id = self.utils.get_contract_id(self, self.echo_acc0, self.create_contract,
                                                 self.__database_api_identifier)

        lcc.set_step("Call 'deploy_contract' method")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.deploy_contract, callee=contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
        contract_result = self.get_contract_result(broadcast_result, self.__database_api_identifier)
        created_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
        lcc.log_info("Output is '{}'".format(created_contract_id))

        lcc.set_step("Subscribe contract created by another contract")
        response_id = self.send_request(self.get_request("subscribe_contracts", [[created_contract_id]]),
                                        self.__database_api_identifier)
        self.get_response(response_id)

        lcc.set_step("Call 'get_creator' method of contract created by another contract")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.get_creator, callee=created_contract_id)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        lcc.set_step("Get notices about updates of contract created by another contract")
        notice = self.get_notice(subscription_callback_id, object_id=self.get_implementation_object_type(
            self.echo.config.implementation_object_types.CONTRACT_HISTORY))

        lcc.set_step("Get contract history")
        operation_history_id = self.get_contract_history(created_contract_id, log_response=True)["result"][0]["id"]

        lcc.set_step("Check notice about updated contract history created by another contract")
        with this_dict(notice):
            check_that_entry("contract", equal_to(created_contract_id))
            check_that_entry("operation_id", equal_to(operation_history_id))

        lcc.set_step("Call 'tr_asset_to_creator' method of created contract")
        operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=self.echo_acc0,
                                                              bytecode=self.tr_asset_to_creator,
                                                              callee=created_contract_id, value_amount=1)
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)
        self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)

        # todo: add info balance_obj. Improve: ECHO-815
        lcc.set_step("Get notices about updates of contract created by another contract")
        notice = self.get_notice(subscription_callback_id, notices_list=True)

        lcc.set_step("Get contract history")
        response = self.get_contract_history(created_contract_id, limit=2, log_response=True)["result"]

        lcc.set_step("Check notice about updated contract history created by another contract")
        self.check_operations_ids_in_notice(response, notice, created_contract_id)
