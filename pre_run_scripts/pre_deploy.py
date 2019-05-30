# -*- coding: utf-8 -*-
import json

from project import ECHO_INITIAL_BALANCE, NATHAN, INITIAL_ACCOUNTS_COUNT, INITIAL_ACCOUNTS_NAMES, \
    ACCOUNT_PREFIX, DEFAULT_ACCOUNTS_COUNT, MAIN_TEST_ACCOUNT_COUNT, WALLETS, INITIAL_ACCOUNTS_ETH_ADDRESSES

BALANCE_TO_ACCOUNT = ECHO_INITIAL_BALANCE / (INITIAL_ACCOUNTS_COUNT + MAIN_TEST_ACCOUNT_COUNT)


def make_all_default_accounts_echo_holders(base_test, nathan_id, database_api):
    list_operations = []
    for i in range(DEFAULT_ACCOUNTS_COUNT - 1):
        to_account_id = get_account_id(get_account(base_test, ACCOUNT_PREFIX + str(i), database_api))
        operation = base_test.echo_ops.get_transfer_operation(base_test.echo, nathan_id, to_account_id, 1,
                                                              signer=NATHAN)
        collected_operation = base_test.collect_operations(operation, database_api)
        list_operations.append(collected_operation)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def add_balance_to_main_test_account(base_test, nathan_id, database_api):
    to_account_id = get_account_id(get_account(base_test, base_test.echo_acc0, database_api))
    operation = base_test.echo_ops.get_transfer_operation(base_test.echo, nathan_id, to_account_id,
                                                          BALANCE_TO_ACCOUNT,
                                                          signer=NATHAN)
    collected_operation = base_test.collect_operations(operation, database_api)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def upgrade_main_test_account_to_lifetime_member(base_test, database_api):
    to_account_id = get_account_id(get_account(base_test, base_test.echo_acc0, database_api))
    operation = base_test.echo_ops.get_account_upgrade_operation(base_test.echo, to_account_id,
                                                                 upgrade_to_lifetime_member=True)
    collected_operation = base_test.collect_operations(operation, database_api)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def get_account_count(base_test, database_api):
    response_id = base_test.send_request(base_test.get_request("get_account_count"), database_api)
    return base_test.get_response(response_id)["result"]


def register_default_accounts(base_test, database_api):
    main_account_count = get_account_count(base_test, database_api)
    list_operations = []
    for i in range(DEFAULT_ACCOUNTS_COUNT):
        names = ACCOUNT_PREFIX + str(i)
        public_data = base_test.store_new_account(names)
        operation = base_test.echo_ops.get_account_create_operation(base_test.echo, names, public_data[0],
                                                                    public_data[0], public_data[1], signer=NATHAN)
        collected_operation = base_test.collect_operations(operation, database_api)
        list_operations.append(collected_operation)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                    log_broadcast=False)
    if not base_test.is_operation_completed(broadcast_result, expected_static_variant=1):
        raise Exception("Default accounts are not created")
    for i in range(DEFAULT_ACCOUNTS_COUNT):
        account_id = broadcast_result.get("trx").get("operation_results")[i][1]
        names = ACCOUNT_PREFIX + str(i)
        with open(WALLETS, "r") as file:
            data = json.load(file)
            data[names].update({"id": account_id})
            with open(WALLETS, "w") as new_file:
                new_file.write(json.dumps(data))
    after_creation_count = get_account_count(base_test, database_api)
    return (after_creation_count - main_account_count) == DEFAULT_ACCOUNTS_COUNT


def distribute_balance_between_main_accounts(base_test, nathan_id, database_api):
    list_operations = []
    for i in range(INITIAL_ACCOUNTS_COUNT):
        if INITIAL_ACCOUNTS_NAMES[i] != "nathan":
            to_account_id = get_account_id(get_account(base_test, INITIAL_ACCOUNTS_NAMES[i], database_api))
            operation = base_test.echo_ops.get_transfer_operation(base_test.echo, nathan_id, to_account_id,
                                                                  BALANCE_TO_ACCOUNT, signer=NATHAN)
            collected_operation = base_test.collect_operations(operation, database_api)
            list_operations.append(collected_operation)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=list_operations,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def distribute_balance_between_committee_addresses(base_test):
    # default_account_balance = base_test.web3.fromWei(base_test.web3.eth.getBalance(base_test.web3.eth.accounts[0]),
    #                                                  "ether")
    default_account_balance = base_test.utils.get_address_balance_in_eth_network(base_test,
                                                                                 base_test.web3.eth.accounts[0])
    # todo: remove
    print("\nDefault account balance in eth: " + str(default_account_balance))
    print("\nAccounts: " + str(base_test.web3.eth.accounts[0]))

    balance_to_transfer = default_account_balance / INITIAL_ACCOUNTS_COUNT

    for i in range(len(INITIAL_ACCOUNTS_ETH_ADDRESSES)):
        transaction = base_test.eth_trx.get_transfer_transaction(web3=base_test.web3,
                                                                 to=INITIAL_ACCOUNTS_ETH_ADDRESSES[i],
                                                                 value=balance_to_transfer)
        base_test.eth_trx.broadcast(web3=base_test.web3, transaction=transaction, debug_mode=True, log_transaction=True)

        # balance = base_test.web3.fromWei(base_test.web3.eth.getBalance(INITIAL_ACCOUNTS_ETH_ADDRESSES[i]), "ether")
        balance = base_test.utils.get_address_balance_in_eth_network(base_test, INITIAL_ACCOUNTS_ETH_ADDRESSES[i])
        print("\nBalance of committee_address #" + str(i) + " in eth: " + str(balance))

    # todo: remove
    default_account_balance = base_test.web3.fromWei(base_test.web3.eth.getBalance(base_test.web3.eth.accounts[0]),
                                                     "ether")
    print("\nMain account NEW balance in eth: " + str(default_account_balance))


def get_public_key(account):
    return account["result"]["active"]["key_auths"][0][0]


def get_account_id(account):
    return account["result"]["id"]


def get_account(base_test, account_name, database_api):
    response_id = base_test.send_request(base_test.get_request("get_account_by_name", [account_name]),
                                         database_api)
    return base_test.get_response(response_id)


def import_balance_to_nathan(base_test, nathan_id, nathan_public_key, database_api):
    operation = base_test.echo_ops.get_balance_claim_operation(base_test.echo, nathan_id, nathan_public_key,
                                                               ECHO_INITIAL_BALANCE, NATHAN)
    collected_operation = base_test.collect_operations(operation, database_api)
    broadcast_result = base_test.echo_ops.broadcast(echo=base_test.echo, list_operations=collected_operation,
                                                    log_broadcast=False)
    return base_test.is_operation_completed(broadcast_result, expected_static_variant=0)


def pre_deploy_echo(base_test, database_api, lcc):
    nathan = get_account(base_test, "nathan", database_api)
    nathan_id = get_account_id(nathan)
    nathan_public_key = get_public_key(nathan)
    distribute_balance_between_committee_addresses(base_test)
    print("\nHERE!!!!!!!!!!!!!!!!")
    if not import_balance_to_nathan(base_test, nathan_id, nathan_public_key, database_api):
        raise Exception("Broadcast failed")
    lcc.log_info("Balance to nathan imported successfully")
    if not distribute_balance_between_main_accounts(base_test, nathan_id, database_api):
        raise Exception("Balance is not distributed")
    lcc.log_info("Balance distributed between main accounts successfully")
    if not register_default_accounts(base_test, database_api):
        raise Exception("Default accounts are not created")
    lcc.log_info("Default accounts created successfully. Accounts count: '{}'".format(DEFAULT_ACCOUNTS_COUNT))
    if not add_balance_to_main_test_account(base_test, nathan_id, database_api):
        raise Exception("Balance to main test account is not credited")
    lcc.log_info("Balance added to main test account ({}) successfully".format(base_test.echo_acc0))
    if not upgrade_main_test_account_to_lifetime_member(base_test, database_api):
        raise Exception("The main test account is not upgraded to the lifetime member")
    lcc.log_info("The main test account upgraded to the lifetime member")
    if not make_all_default_accounts_echo_holders(base_test, nathan_id, database_api):
        raise Exception("Default accounts did not become asset echo holders")
    lcc.log_info("All default accounts became echo holders successfully")
