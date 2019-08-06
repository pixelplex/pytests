# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_none, has_entry

from common.base_test import BaseTest
from common.receiver import Receiver
from project import BASE_URL

SUITE = {
    "description": "Network Broadcast Api"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("network_broadcast_api")
@lcc.suite("Network Broadcast API")
class NetworkBroadcastApi(object):

    @lcc.tags("connection_to_network_broadcast_api", "connection_to_apis")
    @lcc.test("Check connection to NetworkBroadcastApi")
    @lcc.depends_on("DatabaseApi.DatabaseApi.connection_to_database_api",
                    "RegistrationApi.RegistrationApi.connection_to_registration_api")
    def connection_to_network_broadcast_api(self):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base.echo.connect(url=BASE_URL)
        base.receiver = Receiver(web_socket=base.ws)

        lcc.set_step("Requesting access to necessary APIs")
        database_api_identifier = base.get_identifier("database")
        registration_api_identifier = base.get_identifier("registration")

        lcc.set_step("Requesting Access to a Network Broadcast API")
        api_identifier = base.get_identifier("network_broadcast")
        check_that("'network broadcast api identifier'", api_identifier, is_integer())

        lcc.set_step("Check node status, if empty run pre-deploy")
        base.check_node_status()

        lcc.set_step("Get two default account ids")
        echo_acc0 = base.get_account_id(base.accounts[0], database_api_identifier, registration_api_identifier)
        echo_acc1 = base.get_account_id(base.accounts[1], database_api_identifier, registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(echo_acc0, echo_acc1))

        lcc.set_step("Get transaction object")
        transfer_operation = base.echo_ops.get_transfer_operation(echo=base.echo, from_account_id=echo_acc0,
                                                                  to_account_id=echo_acc1)
        collected_operation = base.collect_operations(transfer_operation, database_api_identifier)
        transaction_object = base.echo_ops.broadcast(echo=base.echo, list_operations=collected_operation,
                                                     no_broadcast=True)

        lcc.set_step(
            "Check Network Broadcast api identifier. Call network broadcast api method 'broadcast_transaction'")
        response_id = base.send_request(base.get_request("broadcast_transaction", [transaction_object]),
                                        api_identifier)
        response = base.get_response(response_id)

        check_that(
            "'call method 'broadcast_transaction''",
            response["result"], is_none(), quiet=True
        )

        lcc.set_step("Check that Network Broadcast api identifier is unique")
        response_id = base.send_request(base.get_request("broadcast_transaction", [transaction_object]),
                                        api_identifier + 1)
        response = base.get_response(response_id, negative=True)

        check_that(
            "'using another identifier gives an error'",
            response, has_entry("error"), quiet=True
        )

        base.echo.disconnect()
        base.ws.close()
