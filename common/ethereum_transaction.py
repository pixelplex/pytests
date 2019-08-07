# -*- coding: utf-8 -*-
import decimal
import json
from copy import deepcopy

import lemoncheesecake.api as lcc

from project import ETHEREUM_OPERATIONS, ETH_CONTRACT_ADDRESS, UNPAID_FEE_METHOD, COMMITTEE, ROPSTEN_PK, ROPSTEN, \
    GANACHE_PK


class EthereumTransactions(object):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_operation_json(variable_name):
        # Return needed operation template from json file
        return deepcopy(ETHEREUM_OPERATIONS[variable_name])

    def get_transfer_transaction(self, web3, _from, _to, value, value_currency="ether", gas=2000000, gas_price=None,
                                 gas_price_currency="gwei", debug_mode=False):
        transfer_props = deepcopy(self.get_operation_json("transfer_operation"))
        if _from[:2] != "0x":
            _from = "0x" + _from
        if _to[:2] != "0x":
            _to = "0x" + _to
        if gas_price is not None:
            transfer_props.update({"gasPrice": web3.toWei(gas_price, gas_price_currency)})
        else:
            gas_price = web3.eth.gasPrice
        transfer_props.update(
            {"from": _from, "nonce": web3.eth.getTransactionCount(_from), "to": web3.toChecksumAddress(_to),
             "value": web3.toWei(value, value_currency), "gas": gas, "gasPrice": gas_price})
        if debug_mode:
            lcc.log_debug("Ethereum transfer operation: \n{}".format(json.dumps(transfer_props, indent=4)))
        return transfer_props

    @staticmethod
    def broadcast(web3, transaction, log_transaction=True, log_transaction_logs=False, debug_mode=False):
        if debug_mode:
            lcc.log_debug("Sent:\n{}".format(json.dumps(transaction, indent=4)))
        signed_transaction = web3.eth.defaultAccount.signTransaction(transaction)
        transaction_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        if log_transaction:
            lcc.log_info("Transaction:\n{}".format(web3.eth.getTransaction(transaction_hash)))
        if log_transaction_logs:
            lcc.log_info("Transaction logs:\n{}".format(web3.eth.getTransactionReceipt(transaction_hash).logs))
        return transaction_hash

    @staticmethod
    def get_address_balance_in_eth_network(web3, account_address, currency="ether"):
        return web3.fromWei(web3.eth.getBalance(account_address), currency)

    def get_part_from_address_balance(self, web3, account_address, currency="ether", percent=5):
        current_balance = self.get_address_balance_in_eth_network(web3, account_address, currency=currency)
        return int('{:.0f}'.format(current_balance / 100 * percent))

    def replenish_balance_of_committee_member(self, web3, from_address, to_address, currency="ether", percent=5):
        balance_to_transfer = self.get_part_from_address_balance(web3, from_address, currency=currency, percent=percent)
        transaction = self.get_transfer_transaction(web3, from_address, to_address, value=balance_to_transfer)
        self.broadcast(web3=web3, transaction=transaction)

    @staticmethod
    def get_unpaid_fee(base_test, web3, account_id):
        eeth_accuracy = "1.000000"
        method_call_result = web3.eth.call(
            {
                "to": web3.toChecksumAddress(ETH_CONTRACT_ADDRESS),
                "data": UNPAID_FEE_METHOD + base_test.get_byte_code_param(account_id)
            }
        )
        method_call_result = float(decimal.Decimal(int(method_call_result.hex()[-64:], 16) / 1e18).quantize(
            decimal.Decimal(eeth_accuracy), rounding=decimal.ROUND_UP))
        return method_call_result

    @staticmethod
    def get_status_of_committee_member(base_test, web3, committee_member_address):
        if committee_member_address[:2] == "0x":
            committee_member_address = committee_member_address[2:]
        method_call_result = web3.eth.call(
            {
                "to": web3.toChecksumAddress(ETH_CONTRACT_ADDRESS),
                "data": COMMITTEE + base_test.get_byte_code_param(committee_member_address)
            }
        )
        return bool(int(method_call_result.hex(), 16))

    @staticmethod
    def deploy_contract_in_ethereum_network(web3, eth_address, contract_abi, contract_bytecode, pass_phrase="pass"):
        private_key = ROPSTEN_PK if ROPSTEN else GANACHE_PK
        list_eth_accounts = web3.geth.personal.listAccounts()
        if eth_address not in list_eth_accounts:
            # Import account using private key and pass phrase
            web3.geth.personal.importRawKey(private_key, pass_phrase)
            list_eth_accounts = web3.geth.personal.listAccounts
        if ROPSTEN:
            for eth_account in list_eth_accounts:
                if eth_account == eth_address:
                    eth_address = eth_account
                    break
            # Unlock account using private key and pass phrase
            web3.geth.personal.unlockAccount(eth_address, pass_phrase)
        # Set pre-funded account as sender
        web3.eth.defaultAccount = eth_address
        # Instantiate and deploy contract
        contract = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        # Submit the transaction that deploys the contract
        tx_hash = contract.constructor().transact()
        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        # Create the contract instance with the newly-deployed address
        contract = web3.eth.contract(
            address=contract_address,
            abi=contract_abi,
        )
        return contract

    @staticmethod
    def get_balance_of(contract_instance, eth_address):
        return contract_instance.functions.balanceOf(eth_address).call()

    @staticmethod
    def transfer(web3, contract_instance, account_eth_address, amount, log_transaction=True,
                 log_transaction_logs=False):
        if account_eth_address[:2] != "0x":
            account_eth_address = "0x" + account_eth_address
        tx_hash = contract_instance.functions.transfer(account_eth_address, amount).transact()
        # Wait for transaction to be mined...
        transfer_result = web3.eth.waitForTransactionReceipt(tx_hash)
        if not transfer_result:
            raise Exception("Transfer ERC20 tokens to account failed.")
        if log_transaction:
            lcc.log_info("Transaction:\n{}".format(web3.eth.getTransaction(tx_hash)))
        if log_transaction_logs:
            lcc.log_info("Transaction logs:\n{}".format(web3.eth.getTransactionReceipt(tx_hash).logs))
        return transfer_result
