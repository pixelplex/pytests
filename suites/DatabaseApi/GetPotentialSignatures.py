# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, has_item, is_true, equal_to

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_potential_signatures'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_potential_signatures")
@lcc.suite("Check work of method 'get_potential_signatures'", rank=1)
class GetPotentialSignatures(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc1 = None

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

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_potential_signatures'")
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

        lcc.set_step("Get active keys info about account")
        response_id = self.send_request(self.get_request("get_accounts", [[self.echo_acc0]]),
                                        self.__database_api_identifier)
        active_keys = self.get_response(response_id)["result"][0]["active"]
        lcc.log_info("Active keys of account '{}' were taken".format(self.echo_acc0))

        expected_keys = [active_keys["key_auths"][0][0]]

        lcc.set_step("Get potential signatures for built transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx.json()]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_potential_signatures' method for built transaction")

        lcc.set_step("Check 'get_potential_signatures' method result")
        require_that(
            "potential keys",
            response["result"], equal_to(expected_keys), quiet=True
        )


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_potential_signatures")
@lcc.suite("Positive testing of method 'get_potential_signatures'", rank=2)
class PositiveTesting(BaseTest):
    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None
        self.__registration_api_identifier = None
        self.echo_acc0 = None
        self.echo_acc3 = None
        self.echo_acc4 = None

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
        self.echo_acc3 = self.get_account_id(self.accounts[3], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc4 = self.get_account_id(self.accounts[4], self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info(
            "Echo accounts are: #1='{}', #2='{}', #3='{}'".format(self.echo_acc0, self.echo_acc3, self.echo_acc4))

    def get_account_active_keys(self, account_id):
        response_id = self.send_request(self.get_request("get_accounts", [[account_id]]),
                                        self.__database_api_identifier)
        account_active_keys = self.get_response(response_id)["result"][0]["active"]
        lcc.log_info("Active keys of account '{}' were taken".format(account_id))
        return account_active_keys

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Add additional account_auths to account and get potential signatures for it")
    @lcc.depends_on("DatabaseApi.GetPotentialSignatures.GetPotentialSignatures.method_main_check")
    def get_potential_signatures_of_accounts_with_additional_account_auths(self):
        lcc.set_step("Get active keys info about account: '{}'".format(self.echo_acc3))
        first_account_active_keys = self.get_account_active_keys(self.echo_acc3)

        lcc.set_step("Get active keys info about account: '{}'".format(self.echo_acc4))
        second_account_active_keys = self.get_account_active_keys(self.echo_acc4)

        lcc.set_step("Update info of '{}' account (add account_auths)".format(self.echo_acc4))
        account_auths = [account_auth[0] for account_auth in second_account_active_keys["account_auths"]]
        account_auths_new_item = [self.echo_acc3, 1]
        if self.echo_acc3 not in account_auths:
            new_active_keys = second_account_active_keys.copy()
            new_active_keys["account_auths"].extend([account_auths_new_item])

            transfer_operation = self.echo_ops.get_transfer_operation(
                echo=self.echo,
                from_account_id=self.echo_acc0,
                to_account_id=self.echo_acc4,
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
                echo=self.echo, account=self.echo_acc4,
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
        lcc.log_info("'account_auths' of '{}' account was updated".format(self.echo_acc4))

        lcc.set_step("Get active keys info about account")
        actual_second_account_active_keys = self.get_account_active_keys(self.echo_acc4)
        require_that(
            "new keys",
            actual_second_account_active_keys["account_auths"], has_item(account_auths_new_item),
            quiet=True
        )

        lcc.set_step("Build transfer transaction and store expected keys")
        transfer_operation = self.echo_ops.get_transfer_operation(echo=self.echo,
                                                                  from_account_id=self.echo_acc4,
                                                                  to_account_id=self.echo_acc3)
        collected_operation = self.collect_operations(transfer_operation, self.__database_api_identifier)
        signed_tx = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation,
                                            no_broadcast=True)
        del signed_tx["signatures"]
        expected_keys = [
            first_account_active_keys["key_auths"][0][0],
            actual_second_account_active_keys["key_auths"][0][0]
        ]
        lcc.log_info("Transaction was built")

        lcc.set_step("Get potential signatures for built transaction")
        response_id = self.send_request(self.get_request("get_potential_signatures", [signed_tx.json()]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call 'get_potential_signatures' method for built transaction")

        lcc.set_step("Check 'get_potential_signatures' method result")
        potential_keys = response["result"]
        require_that(
            "potential keys",
            potential_keys, has_length(len(expected_keys)), quiet=True
        )
        for expected_key in expected_keys:
            require_that(
                "potential_keys",
                potential_keys, has_item(expected_key), quiet=True
            )
        # todo: Add test with 'key_auths' update, BUG ECHO-1031