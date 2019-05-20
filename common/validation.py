# -*- coding: utf-8 -*-
import re

NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 63


class Validator(object):
    id_regex = re.compile(r"^(0|([1-9]\d*\.)){2}(0|([1-9]\d*))$")
    account_id_regex = re.compile(r"^1\.2\.(0|[1-9]\d*)$")
    asset_id_regex = re.compile(r"^1\.3\.(0|[1-9]\d*)$")
    eth_asset_id_regex = re.compile(r"^1.3.1$")
    force_settlement_id_regex = re.compile(r"^1\.4\.[1-9]\d*$")
    committee_member_id_regex = re.compile(r"^1\.5\.(0|[1-9]\d*)$")
    limit_order_id_regex = re.compile(r"^1\.6\.[1-9]\d*$")
    call_order_id_regex = re.compile(r"^1\.7\.[1-9]\d*$")
    custom_id_regex = re.compile(r"^1\.8\.[1-9]\d*$")
    proposal_id_regex = re.compile(r"^1\.9\.[1-9]\d*$")
    operation_history_id_regex = re.compile(r"^1\.10\.(0|[1-9]\d*)$")
    withdraw_permission_id_regex = re.compile(r"^1\.11\.[1-9]\d*$")
    vesting_balance_id_regex = re.compile(r"^1\.12\.[1-9]\d*$")
    balance_id_regex = re.compile(r"^1\.13\.[1-9]\d*$")
    contract_id_regex = re.compile(r"^1\.14\.(0|[1-9]\d*)$")
    contract_result_id_regex = re.compile(r"^1\.15\.[1-9]\d*$")
    block_id_regex = re.compile(r"^1\.16\.[1-9]\d*$")
    transfer_id_regex = re.compile(r"^1\.17\.[1-9]\d*$")
    global_object_id_regex = re.compile(r"^2.0.0$")
    dynamic_global_object_id_regex = re.compile(r"^2.1.0$")
    dynamic_asset_data_id_regex = re.compile(r"^2\.3\.(0|[1-9]\d*)$")
    bit_asset_id_regex = re.compile(r"^2\.4\.(0|[1-9]\d*)$")
    account_balance_id_regex = re.compile(r"^2\.5\.[1-9]\d*$")
    account_statistics_id_regex = re.compile(r"^2\.6\.[0|1-9]\d*$")
    transaction_id_regex = re.compile(r"^2\.7\.[1-9]\d*$")
    block_summary_id_regex = re.compile(r"^2\.8\.[1-9]\d*$")
    account_transaction_history_id_regex = re.compile(r"^2\.9\.[1-9]\d*$")
    chain_property_object_id_regex = re.compile(r"^2.10.0$")
    contract_history_id_regex = re.compile(r"^2\.16\.[1-9]\d*$")
    hex_regex = re.compile(r"^[0-9a-fA-F]+")
    bytecode_regex = re.compile(r"^[\da-fA-F]{8}([\da-fA-F]{64})*$")
    vote_id_type_regex = re.compile(r"^[0-3]:[0-9]+")
    iso8601_regex = re.compile(r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01]"
                               r"[0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$")

    def __init__(self):
        super().__init__()

    def is_object_id(self, value):
        return bool(self.id_regex.match(value) and len(value.split(".")) == 3)

    @staticmethod
    def is_string(value):
        if not isinstance(value, str):
            raise ValueError("Value is not string")
        return True

    @staticmethod
    def is_int(value, x):
        try:
            value = abs(int(value))
            if value > 2 ** x:
                raise Exception("Entered value is greater than this type may contain")
            else:
                return True
        except ValueError:
            "Value is not integer"

    @staticmethod
    def is_uint(value, x):
        try:
            value = int(value)
            if value < 0 or value >= 2 ** x:
                raise Exception("Entered value is greater than this type may contain")
            else:
                return True
        except ValueError:
            "Value is not integer"

    def is_hex(self, value):
        if self.is_string(value):
            return bool(self.hex_regex.match(value))

    def is_bytecode(self, value):
        if self.is_string(value):
            return bool(self.bytecode_regex.match(value))

    def is_bytes(self, value, length):
        return self.is_hex(value) and len(value) == length * 2

    def is_account_id(self, value):
        if self.is_string(value):
            return bool(self.account_id_regex.match(value))

    def is_block_id(self, value):
        if self.is_string(value):
            return bool(self.block_id_regex.match(value))

    def is_asset_id(self, value):
        if self.is_string(value):
            return bool(self.asset_id_regex.match(value))

    def is_eth_asset_id(self, value):
        if self.is_string(value):
            return bool(self.eth_asset_id_regex.match(value))

    def is_force_settlement_id(self, value):
        if self.is_string(value):
            return bool(self.force_settlement_id_regex.match(value))

    def is_committee_member_id(self, value):
        if self.is_string(value):
            return bool(self.committee_member_id_regex.match(value))

    def is_limit_order_id(self, value):
        if self.is_string(value):
            return bool(self.limit_order_id_regex.match(value))

    def is_call_order_id(self, value):
        if self.is_string(value):
            return bool(self.call_order_id_regex.match(value))

    def is_custom_id(self, value):
        if self.is_string(value):
            return bool(self.custom_id_regex.match(value))

    def is_proposal_id(self, value):
        if self.is_string(value):
            return bool(self.proposal_id_regex.match(value))

    def is_operation_history_id(self, value):
        if self.is_string(value):
            return bool(self.operation_history_id_regex.match(value))

    def is_withdraw_permission_id(self, value):
        if self.is_string(value):
            return bool(self.withdraw_permission_id_regex.match(value))

    def is_vesting_balance_id(self, value):
        if self.is_string(value):
            return bool(self.vesting_balance_id_regex.match(value))

    def is_balance_id(self, value):
        if self.is_string(value):
            return bool(self.balance_id_regex.match(value))

    def is_contract_id(self, value):
        if self.is_string(value):
            return bool(self.contract_id_regex.match(value))

    def is_contract_result_id(self, value):
        if self.is_string(value):
            return bool(self.contract_result_id_regex.match(value))

    def is_transfer_id(self, value):
        if self.is_string(value):
            return bool(self.transfer_id_regex.match(value))

    def is_global_object_id(self, value):
        if self.is_string(value):
            return bool(self.global_object_id_regex.match(value))

    def is_dynamic_global_object_id(self, value):
        if self.is_string(value):
            return bool(self.dynamic_global_object_id_regex.match(value))

    def is_dynamic_asset_data_id(self, value):
        if self.is_string(value):
            return bool(self.dynamic_asset_data_id_regex.match(value))

    def is_bit_asset_id(self, value):
        if self.is_string(value):
            return bool(self.bit_asset_id_regex.match(value))

    def is_account_balance_id(self, value):
        if self.is_string(value):
            return bool(self.account_balance_id_regex.match(value))

    def is_account_statistics_id(self, value):
        if self.is_string(value):
            return bool(self.account_statistics_id_regex.match(value))

    def is_transaction_id(self, value):
        if self.is_string(value):
            return bool(self.transaction_id_regex.match(value))

    def is_block_summary_id(self, value):
        if self.is_string(value):
            return bool(self.block_summary_id_regex.match(value))

    def is_account_transaction_history_id(self, value):
        if self.is_string(value):
            return bool(self.account_transaction_history_id_regex.match(value))

    def is_chain_property_object_id(self, value):
        if self.is_string(value):
            return bool(self.chain_property_object_id_regex.match(value))

    def is_contract_history_id(self, value):
        if self.is_string(value):
            return bool(self.contract_history_id_regex.match(value))

    def is_vote_id(self, value):
        if self.is_string(value):
            return bool(self.vote_id_type_regex.match(value))

    def is_uint8(self, value):
        return self.is_uint(value, 8)

    def is_uint16(self, value):
        return self.is_uint(value, 16)

    def is_uint32(self, value):
        return self.is_uint(value, 32)

    def is_uint64(self, value):
        return self.is_uint(value, 64)

    def is_int64(self, value):
        return self.is_int(value, 64)

    def is_uint256(self, value):
        return self.is_int(value, 256)

    @staticmethod
    def is_asset_name(value):
        return bool(value is not None and len(value.split(".")) <= 2 and 3 <= len(value) <= 16 and re.match(
            r"^[A-Z][A-Z\d.]*[A-Z]$", value))

    def is_account_name(self, value):
        if not self.is_string(value):
            return False
        if value is None:
            return False
        if len(value) < NAME_MIN_LENGTH or len(value) > NAME_MAX_LENGTH:
            return False

        ref = value.split(".")

        for label in ref:
            if not bool(re.match(r"^[a-z][a-z0-9-]*[a-z\d]$", label)) or bool(re.match(r".*--.*", label)):
                return False
        return True

    def is_ripemd160(self, value):
        return self.is_hex(value) and len(value) == 40

    @staticmethod
    def check_account_name(value):
        if value is None or len(value) == 0:
            raise ValueError("Account name should not be empty.")
        if len(value) < NAME_MIN_LENGTH or len(value) > NAME_MAX_LENGTH:
            raise ValueError("Account name should be from 3 to 63.")
        for label in range(value.split(".")):
            if not re.match(r"^[~a-z]", str(label)):
                raise ValueError("Each account segment should start with a letter.")
            if not re.match(r"^[~a-z0-9-]*$", str(label)):
                raise ValueError("Each account segment should have only letter, digits or dashes.")
            if re.match(r".*--.*", str(label)):
                raise ValueError("Each account segment should have only one dash in a row.")
            if not re.match(r"[a-z0-9]$", str(label)):
                raise ValueError("Each account segment should end with a letter or digit.")
            if len(str(label)) < NAME_MIN_LENGTH:
                raise ValueError("Each account segment should be longer.")
        return True

    def is_operation_id(self, value):
        return self.is_uint8(value) and value < 49

    def is_echo_rand_key(self, value, echo_rand_prefix="DET"):
        if not self.is_hex(value) or len(value) != 44 + len(echo_rand_prefix):
            return False
        prefix = value[0:len(echo_rand_prefix)]
        return echo_rand_prefix == prefix

    def is_private_key(self, value):
        if not self.is_hex(value) or len(value) != 51:
            return False
        return True

    def is_public_key(self, value, address_prefix="ECHO"):
        if not self.is_hex(value) or len(value) != 39 + len(address_prefix):
            return False
        prefix = value[0:len(address_prefix)]
        return address_prefix == prefix

    def is_iso8601(self, value):
        if self.is_string(value):
            return bool(self.iso8601_regex.match(value))
