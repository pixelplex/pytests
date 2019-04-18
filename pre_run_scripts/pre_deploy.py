# -*- coding: utf-8 -*-
from project import ECHO_POOL, NATHAN, DEFAULT_INIT_ACCOUNTS, DEFAULT_ACCOUNT_PREFIX, DEFAULT_ACCOUNT_COUNT, \
    MAIN_TEST_ACCOUNT_COUNT

BALANCE_TO_ACCOUNT = ECHO_POOL / (DEFAULT_INIT_ACCOUNTS + MAIN_TEST_ACCOUNT_COUNT + 1)


def get_main_test_account_id(base_test, database_api):
    response_id = base_test.send_request(base_test.get_request("get_account_by_name", [base_test.echo_acc1]),
                                         database_api)
    return base_test.get_response(response_id)["result"]["id"]


def add_balance_to_main_test_account(base_test, nathan_id, database_api):
    to_account_id = get_main_test_account_id(base_test, database_api)
    operation = base_test.echo_ops.get_transfer_operation(base_test.echo, nathan_id, to_account_id, BALANCE_TO_ACCOUNT,
                                                          signer=NATHAN)
    collected_operation = base_test.collect_operations(operation, database_api)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def register_default_accounts(base_test, database_api):
    response_id = base_test.send_request(base_test.get_request("get_account_count"), database_api)
    main_account_count = base_test.get_response(response_id)["result"]
    list_operations = []
    for i in range(DEFAULT_ACCOUNT_COUNT):
        names = DEFAULT_ACCOUNT_PREFIX + str(i + 1)
        public_data = base_test.store_new_account(names)
        operation = base_test.echo_ops.get_account_create_operation(base_test.echo, names, public_data[0],
                                                                    public_data[0], public_data[1], public_data[0],
                                                                    signer=NATHAN, debug_mode=True)
        collected_operation = base_test.collect_operations(operation, database_api)
        list_operations.append(collected_operation)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                    log_broadcast=True)  # todo !!!
    if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
        raise Exception("Default accounts are not created")
    response_id = base_test.send_request(base_test.get_request("get_account_count"), database_api)
    response = base_test.get_response(response_id)["result"]
    return (response - main_account_count) == DEFAULT_ACCOUNT_COUNT


def distribute_balance_between_main_accounts(base_test, nathan_id, database_api):
    list_operations = []
    for i in range(DEFAULT_INIT_ACCOUNTS):
        to_account_id = get_init_id(base_test, "init" + str(i), database_api)
        operation = base_test.echo_ops.get_transfer_operation(base_test.echo, nathan_id, to_account_id,
                                                              BALANCE_TO_ACCOUNT, signer=NATHAN)
        collected_operation = base_test.collect_operations(operation, database_api)
        list_operations.append(collected_operation)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def get_init_id(base_test, init, database_api):
    response_id = base_test.send_request(base_test.get_request("get_account_by_name", [init]), database_api)
    return base_test.get_response(response_id)["result"]["id"]


def get_nathan(base_test, database_api):
    response_id = base_test.send_request(base_test.get_request("get_account_by_name", ["nathan"]), database_api)
    return base_test.get_response(response_id)


def import_balance_to_nathan(base_test, nathan_id, nathan_public_key, database_api):
    operation = base_test.echo_ops.get_balance_claim_operation(base_test.echo, nathan_id, nathan_public_key,
                                                               ECHO_POOL, NATHAN)
    collected_operation = base_test.collect_operations(operation, database_api)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def pre_deploy_echo(base_test, database_api, lcc):
    nathan = get_nathan(base_test, database_api)
    nathan_id = nathan["result"]["id"]
    nathan_public_key = nathan["result"]["owner"]["key_auths"][0][0]
    if not import_balance_to_nathan(base_test, nathan_id, nathan_public_key, database_api):
        raise Exception("Broadcast failed")
    lcc.log_info("Balance to nathan imported successfully")
    if not distribute_balance_between_main_accounts(base_test, nathan_id, database_api):
        raise Exception("Balance is not distributed")
    lcc.log_info("Balance distributed between main accounts successfully")
    if not register_default_accounts(base_test, database_api):
        raise Exception("Default accounts are not created")
    lcc.log_info("Default accounts created successfully. Accounts count: '{}'".format(DEFAULT_ACCOUNT_COUNT))
    if not add_balance_to_main_test_account(base_test, nathan_id, database_api):
        raise Exception("Balance to main test account is not credited")
    lcc.log_info("Balance added to main test account ({}) successfully. Accounts count: '{}'".format(DEFAULT_ACCOUNT_COUNT))
