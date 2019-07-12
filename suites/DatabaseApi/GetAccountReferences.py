# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import require_that, has_length, has_item, is_true, equal_to, is_list

from common.base_test import BaseTest

SUITE = {
    "description": "Method 'get_account_references'"
}


@lcc.prop("testing", "main")
@lcc.prop("testing", "positive")
@lcc.prop("testing", "negative")
@lcc.tags("database_api", "get_account_references")
@lcc.suite("Check work of method 'get_account_references'", rank=1)
class GetAccountReferences(BaseTest):

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
        self.echo_acc2 = self.get_account_id(self.echo_acc2, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}'".format(self.echo_acc2))

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.prop("type", "method")
    @lcc.test("Simple work of method 'get_account_references'")
    def method_main_check(self):
        lcc.set_step("Get account references")
        response_id = self.send_request(self.get_request("get_account_references", [self.echo_acc2]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id, log_response=True)
        lcc.log_info("Call method 'get_account_references' with account_id='{}' parameter".format(self.echo_acc2))

        lcc.set_step("Check 'get_account_references' method result")
        require_that(
            "account references",
            response["result"], is_list([]), quiet=True
        )


@lcc.prop("testing", "positive")
@lcc.tags("database_api", "get_account_references")
@lcc.suite("Positive testing of method 'get_account_references'", rank=2)
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
        self.echo_acc3 = self.get_account_id(self.echo_acc3, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        self.echo_acc4 = self.get_account_id(self.echo_acc4, self.__database_api_identifier,
                                             self.__registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(self.echo_acc3, self.echo_acc4))

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
    @lcc.test("Add additional account_auths to account and get references of added account")
    @lcc.depends_on("DatabaseApi.GetAccountReferences.GetAccountReferences.method_main_check")
    def get_references_of_account_that_added_to_another_account_auths(self):
        second_account_active_keys = self.get_account_active_keys(self.echo_acc4)
        account_auths = [account_auth[0] for account_auth in second_account_active_keys["account_auths"]]
        account_auths_new_item = [self.echo_acc3, 1]
        lcc.set_step("Update info of {} account (add account_auths)".format(self.echo_acc4))
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

        lcc.log_info("'account_auths' of {} account was updated".format(self.echo_acc4))

        actual_second_account_active_keys = self.get_account_active_keys(self.echo_acc4)
        require_that(
            "new keys",
            actual_second_account_active_keys["account_auths"], has_item(account_auths_new_item),
            quiet=True
        )

        lcc.set_step("Get references of '{}' account".format(self.echo_acc0))
        response_id = self.send_request(self.get_request("get_account_references", [self.echo_acc3]),
                                        self.__database_api_identifier)
        response = self.get_response(response_id)
        lcc.log_info("Call method 'get_account_references' with account_id='{}' parameter".format(self.echo_acc3))

        lcc.set_step("Check 'get_account_references' method result")
        require_that(
            "references of '{}' account".format(self.echo_acc3),
            response["result"],
            is_list([self.echo_acc4]),
            quiet=True
        )

        # todo: Add test with 'key_auths' updating, BUG ECHO-1031
