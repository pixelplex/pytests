# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, has_item, is_true, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_required_signatures'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_required_signatures")
@lcc.suite("Check work of method 'get_required_signatures'", rank=1)
class GetRequiredSignatures(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        self.__registration_api_identifier = self.get_identifier("registration")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))
        lcc.log_info("Registration API identifier is '{}'".format(self.__registration_api_identifier))
        self.echo_acc0 = self.get_account_id(self.echo_acc0, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0))

    def get_account_active_keys(self, account_id):
        lcc.set_step("Get active keys info about account: {}".format(account_id))
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)

        account_active_keys = response["result"][0]["active"]

        lcc.log_info("Active keys of account {} were taken".format(account_id))

        return account_active_keys

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_required_signatures'")
    def method_main_check(self, get_random_valid_account_name):
        first_account_active_keys = self.get_account_active_keys(self.echo_acc0)

        lcc.set_step("Register new account")
        account_name = get_random_valid_account_name
        broadcast_result = self.register_account(
            account_name,
            self.__registration_api_identifier,
            self.__database_api_identifier
        )
        created_account_id = broadcast_result["result"]["id"]
        lcc.log_info("New account id: {}".format(created_account_id))

        created_account_active_keys = self.get_account_active_keys(created_account_id)

        lcc.set_step("Send ECHO ASSETS to new account")
        needed_amount = 3000000
        transfer_operation = self.echo_ops.get_transfer_operation(
            echo=self.echo,
            from_account_id=self.echo_acc0,
            to_account_id=created_account_id,
            amount=needed_amount
        )
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        require_that(
            "transfer to created account complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )
        lcc.log_info("{} of ECHO ASSETS was sent to new account".format(needed_amount))

        lcc.set_step("Update new account active keys")

        new_active_keys = created_account_active_keys.copy()

        # SET NEW VALUES
        lcc.log_info("echo_acc0 pk: {}".format(first_account_active_keys["key_auths"][0][0]))
        new_active_keys["account_auths"] = [
            [self.echo_acc0, 2]
        ]
        new_active_keys["weight_threshold"] = 2

        lcc.log_info("{}".format(new_active_keys))

        operation = self.echo_ops.get_account_update_operation(
            echo=self.echo, account=created_account_id,
            key_auths=new_active_keys["key_auths"],
            account_auths=new_active_keys["account_auths"],
            weight_threshold=new_active_keys["weight_threshold"]
        )
        collected_operation = self.collect_operations(operation, self.__database_api_identifier)

        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                   log_broadcast=False)
        require_that(
            "update of created account complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        actual_active_keys = self.get_account_active_keys(created_account_id)

        lcc.log_info("NEW ACTIVE KEYS: {}".format(actual_active_keys))

        lcc.set_step("Build transaction")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=created_account_id,
                                                                  to_account_id=self.echo_acc0,
                                                                  signer=self.echo_acc0)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        broadcast_result, signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                              get_signed_tx=True)
        require_that(
            "transfer to created account complete successfully",
            self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
        )

        del signed_tx["signatures"]
        lcc.log_info("Transaction was built")
        lcc.set_step("Call 'get_potential_signatures' method  for builded transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx.json()]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)

        lcc.set_step("Call 'get_required_signatures' method  for builded transaction")
        response_id = self.send_request(self.get_request("get_required_signatures", [signed_tx.json(), sorted(response["result"], reverse=True)]),
                                        self.__database_api_identifier)
        response1 = self.get_response(response_id, log_response=True)

        require_that(
            "Proof of wrong 'get_required_signatures' method result",
            response1["result"], equal_to(response["result"])
        )
