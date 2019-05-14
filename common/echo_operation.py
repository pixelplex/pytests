# -*- coding: utf-8 -*-
import json
from copy import deepcopy

import lemoncheesecake.api as lcc

from common.validation import Validator

from project import WALLETS, ECHO_OPERATIONS


class EchoOperations(object):

    def __init__(self):
        super().__init__()
        self.validator = Validator()

    def get_signer(self, signer):
        """
        :param signer: name, id or private_key
        """
        if self.validator.is_echo_rand_key(signer):
            return signer
        wallets = json.load(open(WALLETS))
        if self.validator.is_account_name(signer):
            return wallets[signer]["private_key"]
        if self.validator.is_account_id(signer):
            wallets_keys = list(wallets.keys())
            for key in range(len(wallets_keys)):
                if wallets[wallets_keys[key]]["id"] == signer:
                    return wallets[wallets_keys[key]]["private_key"]
        lcc.log_error("Try to get invalid signer, get: '{}'".format(signer))
        raise Exception("Try to get invalid signer")

    @staticmethod
    def get_operation_json(variable_name, example=False):
        # Return needed operation template from json file
        if example:
            return ECHO_OPERATIONS[variable_name]
        return ECHO_OPERATIONS[variable_name][1]

    def get_transfer_operation(self, echo, from_account_id, to_account_id, amount=1, fee_amount=0, fee_asset_id="1.3.0",
                               amount_asset_id="1.3.0", with_memo=False, from_memo="", to_memo="", nonce_memo="",
                               message="", signer=None, debug_mode=False):
        operation_id = echo.config.operation_ids.TRANSFER
        if with_memo:
            transfer_props = deepcopy(self.get_operation_json("transfer_operation_with_memo"))
            transfer_props["memo"].update({"from": from_memo, "to": to_memo, "nonce": nonce_memo, "message": message})
        else:
            transfer_props = deepcopy(self.get_operation_json("transfer_operation"))
        transfer_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        transfer_props.update({"from": from_account_id, "to": to_account_id})
        transfer_props["amount"].update({"amount": amount, "asset_id": amount_asset_id})
        if debug_mode:
            lcc.log_debug("Transfer operation: \n{}".format(json.dumps(transfer_props, indent=4)))
        if signer is None:
            return [operation_id, transfer_props, from_account_id]
        return [operation_id, transfer_props, signer]

    def get_account_create_operation(self, echo, name, active_key_auths, ed_key, options_memo_key,
                                     fee_amount=0, fee_asset_id="1.3.0", registrar="1.2.12", referrer="1.2.12",
                                     referrer_percent=7500, active_weight_threshold=1, active_account_auths=None,
                                     options_voting_account="1.2.5", options_delegating_account="1.2.12",
                                     options_num_committee=0, options_votes=None, options_extensions=None, signer=None,
                                     debug_mode=False):
        if isinstance(active_key_auths, str):
            active_key_auths = [[active_key_auths, 1]]
        if active_account_auths is None:
            active_account_auths = []
        if options_votes is None:
            options_votes = []
        if options_extensions is None:
            options_extensions = []
        operation_id = echo.config.operation_ids.ACCOUNT_CREATE
        account_create_props = deepcopy(self.get_operation_json("account_create_operation"))
        account_create_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        account_create_props.update(
            {"registrar": registrar, "referrer": referrer, "referrer_percent": referrer_percent, "name": name,
             "ed_key": ed_key})
        account_create_props["active"].update(
            {"weight_threshold": active_weight_threshold, "account_auths": active_account_auths,
             "key_auths": active_key_auths})
        account_create_props["options"].update(
            {"memo_key": options_memo_key, "voting_account": options_voting_account,
             "delegating_account": options_delegating_account, "num_committee": options_num_committee,
             "votes": options_votes, "extensions": options_extensions})
        if debug_mode:
            lcc.log_debug("Create account operation: \n{}".format(json.dumps(account_create_props, indent=4)))
        if signer is None:
            return [operation_id, account_create_props, registrar]
        return [operation_id, account_create_props, signer]

    def get_account_update_operation(self, echo, account, weight_threshold=None, account_auths=None, key_auths=None,
                                     ed_key=None, memo_key=None, voting_account=None, delegating_account=None,
                                     num_committee=None, votes=None, fee_amount=0, fee_asset_id="1.3.0",
                                     debug_mode=False):
        operation_id = echo.config.operation_ids.ACCOUNT_UPDATE
        account_update_props = deepcopy(self.get_operation_json("account_update_operation"))
        account_update_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        account_update_props.update({"account": account})
        if weight_threshold is not None:
            account_update_props["active"].update(
                {"weight_threshold": weight_threshold, "account_auths": account_auths, "key_auths": key_auths})
        else:
            del account_update_props["active"]
        if ed_key is not None:
            account_update_props.update({"ed_key": ed_key})
        else:
            del account_update_props["ed_key"]
        if voting_account is not None:
            account_update_props["new_options"].update(
                {"memo_key": memo_key, "voting_account": voting_account, "delegating_account": delegating_account,
                 "num_committee": num_committee, "votes": votes})
        else:
            del account_update_props["new_options"]
        if debug_mode:
            lcc.log_debug("Update account operation: \n{}".format(json.dumps(account_update_props, indent=4)))
        return [operation_id, account_update_props, account]

    def get_asset_create_operation(self, echo, issuer, symbol, precision=0, fee_amount=0, fee_asset_id="1.3.0",
                                   max_supply="1000000000000000", market_fee_percent=0,
                                   max_market_fee="1000000000000000",
                                   issuer_permissions=79, flags=0, base_amount=1, base_asset_id="1.3.0",
                                   quote_amount=1, quote_asset_id="1.3.1", whitelist_authorities=None,
                                   blacklist_authorities=None, whitelist_markets=None, blacklist_markets=None,
                                   description="", is_prediction_market=False, signer=None, debug_mode=False):
        if whitelist_authorities is None:
            whitelist_authorities = []
        if blacklist_authorities is None:
            blacklist_authorities = []
        if whitelist_markets is None:
            whitelist_markets = []
        if blacklist_markets is None:
            blacklist_markets = []
        operation_id = echo.config.operation_ids.ASSET_CREATE
        asset_create_props = deepcopy(self.get_operation_json("asset_create_operation"))
        asset_create_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        asset_create_props.update({"issuer": issuer, "symbol": symbol, "precision": precision})
        asset_create_props["common_options"].update({"max_supply": max_supply, "market_fee_percent": market_fee_percent,
                                                     "max_market_fee": max_market_fee,
                                                     "issuer_permissions": issuer_permissions, "flags": flags})
        asset_create_props["common_options"]["core_exchange_rate"]["base"].update(
            {"amount": base_amount, "asset_id": base_asset_id})
        asset_create_props["common_options"]["core_exchange_rate"]["quote"].update(
            {"amount": quote_amount, "asset_id": quote_asset_id})
        asset_create_props["common_options"].update(
            {"whitelist_authorities": whitelist_authorities, "blacklist_authorities": blacklist_authorities,
             "whitelist_markets": whitelist_markets, "blacklist_markets": blacklist_markets,
             "description": description})
        asset_create_props.update({"is_prediction_market": is_prediction_market})
        if debug_mode:
            lcc.log_debug("Create asset operation: \n{}".format(json.dumps(asset_create_props, indent=4)))
        if signer is None:
            return [operation_id, asset_create_props, issuer]
        return [operation_id, asset_create_props, signer]

    def get_asset_issue_operation(self, echo, issuer, value_amount, value_asset_id, issue_to_account, fee_amount=0,
                                  fee_asset_id="1.3.0", signer=None, debug_mode=False):
        operation_id = echo.config.operation_ids.ASSET_ISSUE
        asset_issue_props = deepcopy(self.get_operation_json("asset_issue_operation"))
        asset_issue_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        asset_issue_props.update({"issuer": issuer, "issue_to_account": issue_to_account})
        asset_issue_props["asset_to_issue"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug(
                "Asset issue operation: \n{}".format(json.dumps([operation_id, asset_issue_props], indent=4)))
        if signer is None:
            return [operation_id, asset_issue_props, issuer]
        return [operation_id, asset_issue_props, signer]

    def get_balance_claim_operation(self, echo, deposit_to_account, balance_owner_public_key, value_amount,
                                    balance_owner_private_key, fee_amount=0, fee_asset_id="1.3.0",
                                    balance_to_claim="1.13.0", value_asset_id="1.3.0", debug_mode=False):
        operation_id = echo.config.operation_ids.BALANCE_CLAIM
        balance_claim_operation_props = deepcopy(self.get_operation_json("balance_claim_operation"))
        balance_claim_operation_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        balance_claim_operation_props.update(
            {"deposit_to_account": deposit_to_account, "balance_to_claim": balance_to_claim,
             "balance_owner_key": balance_owner_public_key})
        balance_claim_operation_props["total_claimed"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug(
                "Balance claim operation: \n{}".format(
                    json.dumps([operation_id, balance_claim_operation_props], indent=4)))
        return [operation_id, balance_claim_operation_props, balance_owner_private_key]

    def get_create_contract_operation(self, echo, registrar, bytecode, fee_amount=0, fee_asset_id="1.3.0",
                                      value_amount=0, value_asset_id="1.3.0", supported_asset_id="1.3.0",
                                      eth_accuracy=False, signer=None, debug_mode=False):
        operation_id = echo.config.operation_ids.CREATE_CONTRACT
        create_contract_props = deepcopy(self.get_operation_json("create_contract_operation"))
        create_contract_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        create_contract_props.update(
            {"registrar": registrar, "code": bytecode, "supported_asset_id": supported_asset_id,
             "eth_accuracy": eth_accuracy})
        create_contract_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug(
                "Create contract operation: \n{}".format(json.dumps([operation_id, create_contract_props], indent=4)))
        if signer is None:
            return [operation_id, create_contract_props, registrar]
        return [operation_id, create_contract_props, signer]

    def get_call_contract_operation(self, echo, registrar, bytecode, callee, fee_amount=0, fee_asset_id="1.3.0",
                                    value_amount=0, value_asset_id="1.3.0", signer=None, debug_mode=False):
        operation_id = echo.config.operation_ids.CALL_CONTRACT

        call_contract_props = deepcopy(self.get_operation_json("call_contract_operation"))
        call_contract_props["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
        call_contract_props.update({"registrar": registrar, "code": bytecode, "callee": callee})
        call_contract_props["value"].update({"amount": value_amount, "asset_id": value_asset_id})
        if debug_mode:
            lcc.log_debug("Call contract operation: \n{}".format(json.dumps(call_contract_props, indent=4)))
        if signer is None:
            return [operation_id, call_contract_props, registrar]
        return [operation_id, call_contract_props, signer]

    def broadcast(self, echo, list_operations, log_broadcast=True, debug_mode=False):
        tx = echo.create_transaction()
        if debug_mode:
            lcc.log_debug("List operations:\n{}".format(json.dumps(list_operations, indent=4)))
        if type(list_operations[0]) is int:
            list_operations = [list_operations]
        if len(list_operations) > 1:
            list_operations = [item for sublist in list_operations for item in sublist]
        for i in range(len(list_operations)):
            tx.add_operation(name=list_operations[i][0], props=list_operations[i][1])
        for i in range(len(list_operations)):
            tx.add_signer(self.get_signer(list_operations[i][2]))
        tx.sign()
        broadcast_result = tx.broadcast()
        if log_broadcast:
            lcc.log_info("Broadcast result: \n{}".format(json.dumps(broadcast_result, indent=4)))
        return broadcast_result
