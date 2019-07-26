# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that, is_integer, is_none, has_entry

from common.base_test import BaseTest
from common.receiver import Receiver

SUITE = {
    "description": "Network Broadcast Api"
}


@lcc.prop("suite_run_option_1", "main")
@lcc.tags("network_broadcast_api")
@lcc.suite("Network Broadcast API")
class NetworkBroadcastApi(object):

    @lcc.tags("connection_to_network_broadcast_api")
    @lcc.test("Check connection to NetworkBroadcastApi")
    def connection_to_network_broadcast_api(self):
        base = BaseTest()
        base.ws = base.create_connection_to_echo()
        base._connect_to_echopy_lib()

        base.receiver = Receiver(web_socket=base.ws)
        lcc.set_step("Requesting access to necessary Api's")
        network_broadcast_identifier = base.get_identifier("network_broadcast")
        database_api_identifier = base.get_identifier("database")
        registration_api_identifier = base.get_identifier("registration")
        lcc.log_info(
            "API identifiers are: network_broadcast='{}', database='{}', registration='{}'".format(
                network_broadcast_identifier,
                database_api_identifier,
                registration_api_identifier))
        check_that("'network broadcast api identifier'", network_broadcast_identifier, is_integer())
        check_that("'network broadcast api identifier'", database_api_identifier, is_integer())
        check_that("'network broadcast api identifier'", registration_api_identifier, is_integer())

        lcc.set_step("Get two account ids")
        echo_acc0 = base.get_account_id(base.accounts[0], database_api_identifier,
                                        registration_api_identifier)
        echo_acc1 = base.get_account_id(base.accounts[1], database_api_identifier,
                                        registration_api_identifier)
        lcc.log_info("Echo accounts are: #1='{}', #2='{}'".format(echo_acc0, echo_acc1))
        lcc.set_step("Create an operation without broadcast")
        transfer_operation = base.echo_ops.get_transfer_operation(echo=base.echo,
                                                                  from_account_id=echo_acc0,
                                                                  to_account_id=echo_acc1)
        collected_operation = base.collect_operations(transfer_operation, database_api_identifier)
        broadcast_obj = base.echo_ops.broadcast(echo=base.echo, list_operations=collected_operation,
                                                no_broadcast=True)

        lcc.set_step("Check Network Broadcast api identifier. Call network broadcast api method 'broadcast_transaction'")
        response_id = base.send_request(base.get_request("broadcast_transaction",
                                                         [broadcast_obj.json()]),
                                        network_broadcast_identifier)
        response = base.get_response(response_id, log_response=True)

        check_that(
            "'call method 'get_objects''",
            response["result"], is_none(), quiet=True
        )
        base._disconnect_to_echopy_lib()
        base.ws.close()
