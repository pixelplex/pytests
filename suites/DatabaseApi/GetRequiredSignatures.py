# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_item, is_true, equal_to

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
        self.echo_acc1 = self.get_account_id(self.echo_acc1, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc0, self.echo_acc1))

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
    def method_main_check(self):
        lcc.set_step("Build transfer transaction")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc0,
                                                                  to_account_id=self.echo_acc1)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)

        del signed_tx["signatures"]
        lcc.log_info("Transaction was built")

        active_keys = self.get_account_active_keys(self.echo_acc0)
        expected_keys = [active_keys["key_auths"][0][0]]

        lcc.set_step("Get potential signatures for builded transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx.json()]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_potential_signatures' method for builded transaction")

        lcc.set_step("Check 'get_potential_signatures' method result")
        require_that(
            "potential keys",
            response["result"], equal_to(expected_keys), quiet=True
        )

        lcc.set_step("Get required signatures for bulded transaction")
        response_id = self.send_request(
            self.get_request(
                "get_required_signatures",
                [signed_tx.json(), expected_keys]
            ),
            self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info(
            "Call 'get_required_signatures' method for builded transaction and keys from 'get_potential_signatures' method"
        )

        lcc.set_step("Check 'get_required_signatures' method result")
        require_that(
            "required keys",
            response["result"], equal_to(expected_keys), quiet=True
        )


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_required_signatures")
@lcc.suite("Positive testing of method 'get_required_signatures'", rank=2)
class PositiveTesting(BaseTest):
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
        self.echo_acc14 = self.get_account_id(self.echo_acc14, self.__database_api_identifier,
                                              self.__registration_api_identifier)
        self.echo_acc15 = self.get_account_id(self.echo_acc15, self.__database_api_identifier,
                                              self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0,
                                                                           self.echo_acc14,
                                                                           self.echo_acc15))

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
    @lcc.test("Add additional account_auths and change weight_threshold to account and get required signatures for it")
    @lcc.depends_on("DatabaseApi.GetRequiredSignatures.GetRequiredSignatures.method_main_check")
    def get_potential_signatures_of_accounts_with_additional_account_auths(self):
        first_account_active_keys = self.get_account_active_keys(self.echo_acc14)
        second_account_active_keys = self.get_account_active_keys(self.echo_acc15)
        account_auths = [account_auth[0] for account_auth in second_account_active_keys["account_auths"]]
        account_auths_new_item = [self.echo_acc14, 2]
        lcc.set_step("Update info of {} account (add account_auths)".format(self.echo_acc15))
        if self.echo_acc14 not in account_auths:
            new_active_keys = second_account_active_keys.copy()
            new_active_keys["account_auths"].extend([account_auths_new_item])
            new_active_keys["weight_threshold"] = 2

            transfer_operation = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                from_account_id=self.echo_acc0,
                to_account_id=self.echo_acc15,
                amount=3000000
            )
            collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                                       log_broadcast=False)
            require_that(
                "transfer to created account complete successfully",
                self.is_operation_completed(broadcast_result, 0), is_true(), quiet=True
            )

            operation = self.echo_ops.get_account_update_operation(
                echo=self.echo, account=self.echo_acc15,
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

        lcc.log_info("'account_auths' of {} account was updated".format(self.echo_acc15))

        actual_second_account_active_keys = self.get_account_active_keys(self.echo_acc15)
        require_that(
            "new keys",
            actual_second_account_active_keys["account_auths"], has_item(account_auths_new_item),
            quiet=True
        )

        lcc.set_step("Build transfer transaction")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc15,
                                                                  to_account_id=self.echo_acc14)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        del signed_tx["signatures"]
        lcc.log_info("Transaction was built")

        expected_keys = [
            first_account_active_keys["key_auths"][0][0]
        ]

        lcc.set_step("Get potential signatures for builded transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx.json()]),
                                        self.__database_api_identifier)
        potential_keys = self.get_response(response_id)["result"]
        lcc.log_info("Call 'get_potential_signatures' method for builded transaction")

        lcc.set_step("Get required signatures for builded transaction with pontential keys")
        response_id = self.send_request(
            self.get_request(
                "get_required_signatures",
                [signed_tx.json(), potential_keys]
            ),
            self.__database_api_identifier
        )
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_required_signatures' method for builded transaction with potential keys")

        lcc.set_step("Check 'get_required_signatures' method result")
        require_that(
            "required keys",
            response["result"], equal_to(expected_keys), quiet=True
        )

        # todo: Add test with 'key_auths' update, BUG ECHO-1031
