# -*- coding: utf-8 -*-
import json
from copy import deepcopy

import lemoncheesecake.api as lcc

from project import ETHEREUM_OPERATIONS, ETH_PRIVATE_KEY


class EthereumTransactions(object):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_operation_json(variable_name):
        # Return needed operation template from json file
        return ETHEREUM_OPERATIONS[variable_name]

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
