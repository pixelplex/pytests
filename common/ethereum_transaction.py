# -*- coding: utf-8 -*-
import json
from copy import deepcopy

import lemoncheesecake.api as lcc

from project import ETHEREUM_OPERATIONS, ETH_PRIVATE_KEY, ETH_CONTRACT_ADDRESS, UNPAID_FEE_METHOD, COMMITTEE


class EthereumTransactions(object):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_operation_json(variable_name):
        # Return needed operation template from json file
        return deepcopy(ETHEREUM_OPERATIONS[variable_name])

    def get_transfer_transaction(self, web3, to, value, _from=None, nonce=None, value_currency="ether", gas=2000000,
                                 gas_price=None, gas_price_currency="gwei", signer=ETH_PRIVATE_KEY, debug_mode=False):
        transfer_props = deepcopy(self.get_operation_json("transfer_operation"))
        if _from is not None:
            transfer_props.update({"from": _from})
        if to[:2] != "0x":
            to = "0x" + to
        if nonce is None:
            nonce = web3.eth.getTransactionCount(web3.eth.accounts[0])
        if gas_price is not None:
            transfer_props.update({"gasPrice": web3.toWei(gas_price, gas_price_currency)})
        else:
            gas_price = web3.eth.gasPrice
        transfer_props.update(
            {"nonce": nonce, "to": web3.toChecksumAddress(to), "value": web3.toWei(value, value_currency), "gas": gas,
             "gasPrice": gas_price})
        if debug_mode:
            lcc.log_debug("Ethereum transfer operation: \n{}".format(json.dumps(transfer_props, indent=4)))
        return [transfer_props, signer]

    @staticmethod
    def broadcast(web3, transaction, log_transaction=True, log_transaction_logs=False, debug_mode=False):
        if debug_mode:
            lcc.log_debug("Sent:\n{}".format(json.dumps(transaction, indent=4)))
        signed_transaction = web3.eth.account.signTransaction(transaction[0], transaction[1])
        transaction_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        if log_transaction:
            lcc.log_info("Transaction:\n{}".format(web3.eth.getTransaction(transaction_hash)))
        if log_transaction_logs:
            lcc.log_info("Transaction logs:\n{}".format(web3.eth.getTransactionReceipt(transaction_hash).logs))

    @staticmethod
    def get_address_balance_in_eth_network(web3, account_address, currency="ether"):
        return web3.fromWei(web3.eth.getBalance(account_address), currency)

    def get_part_from_address_balance(self, web3, account_address, currency="ether", percent=5):
        current_balance = self.get_address_balance_in_eth_network(web3, account_address, currency=currency)
        return int('{:.0f}'.format(current_balance / 100 * percent))

    def replenish_balance_of_committee_member(self, web3, from_address, to_address, currency="ether", percent=5):
        balance_to_transfer = self.get_part_from_address_balance(web3, from_address, currency=currency, percent=percent)
        transaction = self.get_transfer_transaction(web3, to_address, value=balance_to_transfer)
        self.broadcast(web3=web3, transaction=transaction)

    @staticmethod
    def get_unpaid_fee(base_test, account_id, in_ethereum=False):
        method_call_result = base_test.web3.eth.call(
            {
                "to": base_test.web3.toChecksumAddress(ETH_CONTRACT_ADDRESS),
                "data": UNPAID_FEE_METHOD + base_test.get_byte_code_param(account_id)
            }
        )
        if in_ethereum:
            return round(int(method_call_result.hex()[-64:], 16) / 1e18, 6)
        return round(int(method_call_result.hex()[-64:], 16) / 1e12)

    @staticmethod
    def get_status_of_committee_member(base_test, committee_member_address):
        if committee_member_address[:2] == "0x":
            committee_member_address = committee_member_address[2:]
        method_call_result = base_test.web3.eth.call(
            {
                "to": base_test.web3.toChecksumAddress(ETH_CONTRACT_ADDRESS),
                "data": COMMITTEE + base_test.get_byte_code_param(committee_member_address)
            }
        )
        return bool(int(method_call_result.hex(), 16))
