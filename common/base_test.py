# -*- coding: utf-8 -*-
import codecs
import json
import os
import time

import lemoncheesecake.api as lcc
from Crypto.Hash import keccak
from echopy import Echo
from eth_account import Account
from lemoncheesecake.matching import is_str, is_integer, check_that_entry
from web3 import Web3
from websocket import create_connection

from common.echo_operation import EchoOperations
from common.ethereum_transaction import EthereumTransactions
from common.receiver import Receiver
from common.utils import Utils
from common.validation import Validator
from pre_run_scripts.pre_deploy import pre_deploy_echo
from project import RESOURCES_DIR, BASE_URL, ECHO_CONTRACTS, WALLETS, ACCOUNT_PREFIX, ETHEREUM_URL, ETH_ASSET_ID, \
    DEFAULT_ACCOUNTS_COUNT, EXECUTION_STATUS_PATH, BLOCK_RELEASE_INTERVAL, ETHEREUM_CONTRACTS, ROPSTEN, ROPSTEN_PK, \
    GANACHE_PK, DEBUG


class BaseTest(object):

    def __init__(self):
        super().__init__()
        self.ws = None
        self.receiver = None
        self.echo = Echo()
        self.utils = Utils()
        self.web3 = None
        self.echo_ops = EchoOperations()
        self.eth_trx = EthereumTransactions()
        self.__id = 0
        self.validator = Validator()
        self.echo_asset = "1.3.0"
        self.eth_asset = ETH_ASSET_ID
        # Declare all default accounts
        self.accounts = ["{}{}".format(ACCOUNT_PREFIX, account_num) for account_num in range(DEFAULT_ACCOUNTS_COUNT)]

    @staticmethod
    def create_connection_to_echo():
        # Method create connection to Echo network
        return create_connection(url=BASE_URL)

    def get_default_ethereum_account(self):
        if not ROPSTEN:
            self.web3.eth.defaultAccount = Account.privateKeyToAccount(GANACHE_PK)
            return self.web3.eth.defaultAccount
        self.web3.eth.defaultAccount = Account.privateKeyToAccount(ROPSTEN_PK)
        return self.web3.eth.defaultAccount

    def get_object_type(self, object_types):
        # Give object type mask
        return "{}.{}.".format(self.echo.config.reserved_spaces.PROTOCOL_IDS, object_types)

    def get_implementation_object_type(self, implementation_object_types):
        # Give implementation object type mask
        return "{}.{}.".format(self.echo.config.reserved_spaces.IMPLEMENTATION_IDS, implementation_object_types)

    def check_uint64_numbers(self, response, key, quiet=False):
        # Method check uint64 numbers
        if type(response.get(key)) is str:
            self.validator.is_uint64(response.get(key))
            check_that_entry(key, is_str(), quiet=quiet)
        else:
            check_that_entry(key, is_integer(), quiet=quiet)

    def check_uint256_numbers(self, response, key, quiet=False):
        if type(response.get(key)) is str:
            self.validator.is_uint256(response.get(key))
            check_that_entry(key, is_str(), quiet=quiet)
        else:
            check_that_entry(key, is_integer(), quiet=quiet)

    @staticmethod
    def get_time(global_time=False):
        if global_time:
            return time.strftime("%H:%M:%S", time.gmtime())
        return time.strftime("%H:%M:%S", time.localtime())

    @staticmethod
    def get_datetime(global_datetime=False):
        if global_datetime:
            return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())

    def set_timeout_wait(self, seconds=None, wait_block_count=None, print_log=True):
        if wait_block_count is not None:
            seconds = wait_block_count * BLOCK_RELEASE_INTERVAL
        if print_log:
            lcc.log_info("Start a '{}' second(s) sleep..."
                         "\nglobal_time:'{}'"
                         "\nlocal_time:'{}'".format(seconds, self.get_time(global_time=True), self.get_time()))
        time.sleep(seconds)
        if print_log:
            lcc.log_info("Sleep is over.\nglobal_time:'{}'\nlocal_time:'{}'".format(self.get_time(global_time=True),
                                                                                    self.get_time()))

    @staticmethod
    def get_value_for_sorting_func(str_value):
        return int(str_value[str_value.rfind('.') + 1:])

    @staticmethod
    def get_byte_code(contract_name, code_or_method_name, ethereum_contract=False):
        if ethereum_contract:
            return ETHEREUM_CONTRACTS[contract_name][code_or_method_name]
        return ECHO_CONTRACTS[contract_name][code_or_method_name]

    @staticmethod
    def get_abi(contract_name):
        return ETHEREUM_CONTRACTS[contract_name]["abi"]

    def get_byte_code_param(self, param, param_type=None, offset="20"):
        hex_param_64 = "0000000000000000000000000000000000000000000000000000000000000000"
        if param_type == int and self.validator.is_uint256(param):
            param = hex(param).split('x')[-1]
            hex_param = hex_param_64[:-len(param)] + param
            return hex_param
        if param_type == str and self.validator.is_string(param):
            param_in_hex = codecs.encode(param).hex()
            len_param_in_hex = hex(len(param)).split('x')[-1]
            part_1 = hex_param_64[:-2] + offset
            part_2 = hex_param_64[:-len(len_param_in_hex)] + len_param_in_hex
            part_3 = None
            if len(param_in_hex) < 64:
                part_3 = param_in_hex + hex_param_64[:-len(param_in_hex)]
            return part_1 + part_2 + part_3
        if self.validator.is_object_id(param):
            param = hex(int(param.split('.')[2])).split('x')[-1]
            hex_param = hex_param_64[:-len(param)] + param
            return hex_param
        if self.validator.is_eth_address(param):
            return hex_param_64[:-len(param)] + param
        lcc.log_error("Param not valid, got: {}".format(param))
        raise Exception("Param not valid")

    @staticmethod
    def get_file_attachment_path(file_name):
        return os.path.join(RESOURCES_DIR, file_name)

    def add_file_to_report(self, kind, filename, file_description, data=None):
        try:
            if kind == "file" and data is None:
                lcc.set_step("Attachment file")
                lcc.save_attachment_file(self.get_file_attachment_path(filename), file_description)
            elif kind == "image" and data is None:
                lcc.set_step("Image attachment")
                lcc.save_image_file(self.get_file_attachment_path(filename), file_description)
            elif kind == "file" and data is not None:
                lcc.set_step("Attachment file content")
                lcc.save_attachment_content(data, filename, file_description)
            elif kind == "image" and data is not None:
                lcc.set_step("Image attachment content")
                lcc.save_image_content(data, filename, file_description)
        except FileNotFoundError:
            lcc.log_error("File or image does not exist!")

    @staticmethod
    def prepare_attach_to_report(kind, filename, file_description, data):
        try:
            if kind == "file":
                lcc.set_step("Prepare attachment file")
                with lcc.prepare_attachment(filename, file_description) \
                        as file:
                    with open(file, "w") as fh:
                        fh.write(data)
            elif kind == "image":
                lcc.set_step("Prepare image attachment")
                with lcc.prepare_image_attachment(filename, file_description) \
                        as file:
                    with open(file, "w") as fh:
                        fh.write(data)
        except FileNotFoundError:
            lcc.log_error("File or image does not exist!")

    @staticmethod
    def get_request(method_name, params=None):
        # Params must be list
        request = [1, method_name]
        if params is None:
            request.append([])
            return request
        request.extend([params])
        return request

    @staticmethod
    def get_call_template():
        # Return call method format
        return {"id": 0, "method": "call", "params": []}

    def __call_method(self, method, api_identifier=None):
        # Returns the api method call
        self.__id += 1
        call_template = self.get_call_template()
        try:
            if api_identifier is None:
                call_template["id"] = self.__id
                call_template["params"] = method
                return call_template
            call_template["id"] = self.__id
            call_template["params"].append(api_identifier)
            for i in range(1, len(method)):
                call_template["params"].append(method[i])
            return call_template
        except KeyError as key:
            lcc.log_error("Call method: That key does not exist: '{}'".format(key))
        except IndexError as index:
            lcc.log_error("Call method: This index does not exist: '{}'".format(index))

    def send_request(self, request, api_identifier=None, debug_mode=False):
        # Send request to server
        if api_identifier is None:
            method = self.__call_method(request)
            self.ws.send(json.dumps(method))
            if debug_mode:
                lcc.log_debug("Send: {}".format(json.dumps(method, indent=4)))
            return method["id"]
        method = self.__call_method(request, api_identifier)
        self.ws.send(json.dumps(method))
        if debug_mode:
            lcc.log_debug("Send: {}".format(json.dumps(method, indent=4)))
        return method["id"]

    def get_response(self, id_response, negative=False, log_response=False, debug_mode=False):
        # Receive answer from server
        try:
            if debug_mode:
                lcc.log_debug("Parameters: negative={}, ".format(negative))
                response = json.loads(self.ws.recv())
                lcc.log_debug("Received:\n{}".format(json.dumps(response, indent=4)))
                return response
            return self.receiver.get_response(id_response, negative, log_response)
        except KeyError as key:
            lcc.log_error("Response: That key does not exist: '{}'".format(key))
        except IndexError as index:
            lcc.log_error("Response: This index does not exist: '{}'".format(index))

    def get_notice(self, id_response, object_id=None, operation_id=None, notices_list=False, log_response=True,
                   debug_mode=False):
        # Receive notice from server
        try:
            if debug_mode:
                lcc.log_debug("Parameters: object_id={}".format(object_id))
                response = json.loads(self.ws.recv())
                lcc.log_debug("Received:\n{}".format(json.dumps(response, indent=4)))
                return response
            if notices_list:
                notice = json.loads(self.ws.recv())
                if log_response:
                    lcc.log_info("Received notice with list of notifications:\n{}".format(json.dumps(notice, indent=4)))
                return notice["params"][1][0]
            return self.receiver.get_notice(id_response, object_id, operation_id, log_response)
        except KeyError as key:
            lcc.log_error("Notice: That key does not exist: '{}'".format(key))
        except IndexError as index:
            lcc.log_error("Notice: This index does not exist: '{}'".format(index))

    def get_trx_completed_response(self, id_response, debug_mode=False):
        # Receive answer from server that transaction completed
        response = self.get_response(id_response, debug_mode=debug_mode)
        transaction_excepted = response.get("result")[1].get("exec_res").get("excepted")
        if transaction_excepted != "None":
            lcc.log_error("Transaction not completed. Excepted: '{}'".format(transaction_excepted))
            raise Exception("Transaction not completed")
        return response

    def get_identifier(self, api, debug_mode=False):
        # Initialise identifier for api
        call_template = self.get_call_template()
        call_template["params"] = [1, api, []]
        self.ws.send(json.dumps(call_template))
        response = json.loads(self.ws.recv())
        api_identifier = response["result"]
        if debug_mode:
            print("'{}' api identifier is '{}'\n".format(api, api_identifier))
        return api_identifier

    @staticmethod
    def is_completed_operation_return_empty_object(response):
        operations_count = response.get("trx").get("operations")
        if len(operations_count) == 1:
            operation_result = response.get("trx").get("operation_results")[0]
            if operation_result[0] != 0 and operation_result[1] != {}:
                lcc.log_error("Wrong format of operation result, got {}".format(operation_result))
                raise Exception("Wrong format of operation result")
            return True
        operation_results = []
        for i in range(len(operations_count)):
            operation_results.append(response.get("trx").get("operation_results")[i])
            if operation_results[i][0] != 0 and operation_results[i][1] != {}:
                lcc.log_error("Wrong format of operation results, got {}".format(operation_results))
                raise Exception("Wrong format of operation results")
            return True

    def is_completed_operation_return_id(self, response):
        operations_count = response.get("trx").get("operations")
        if len(operations_count) == 1:
            operation_result = response.get("trx").get("operation_results")[0]
            if operation_result[0] != 1 and not self.validator.is_object_id(operation_result[1]):
                lcc.log_error("Wrong format of operation result, got {}".format(operation_result))
                raise Exception("Wrong format of operation result")
            return True
        operation_results = []
        for i in range(len(operations_count)):
            operation_results.append(response.get("trx").get("operation_results")[i])
            if operation_results[i][0] != 1 and not self.validator.is_object_id(operation_results[i][1]):
                lcc.log_error("Wrong format of operation results, got {}".format(operation_results))
                raise Exception("Wrong format of operation results")
            return True

    def is_operation_completed(self, response, expected_static_variant):
        if expected_static_variant == 0:
            return self.is_completed_operation_return_empty_object(response)
        if expected_static_variant == 1:
            return self.is_completed_operation_return_id(response)

    @staticmethod
    def get_operation_results_ids(response):
        operations_count = response.get("trx").get("operations")
        if len(operations_count) == 1:
            operation_result = response.get("trx").get("operation_results")[0]
            if operation_result[0] != 1:
                lcc.log_error("Wrong format of operation result, need [0] = 1, got {}".format(operation_result))
                raise Exception("Wrong format of operation result")
            return operation_result[1]
        operation_results = []
        for i in range(len(operations_count)):
            operation_results.append(response.get("trx").get("operation_results")[i])
            if operation_results[i][0] != 1:
                lcc.log_error("Wrong format of operation results, need [0] = 1, got {}".format(operation_results))
                raise Exception("Wrong format of operation results")
        return operation_results

    def get_contract_id(self, response, contract_call_result=False, address_format=None, new_contract=True):
        if address_format:
            contract_identifier_hex = response
        elif not contract_call_result:
            contract_identifier_hex = response["result"][1]["exec_res"]["new_address"]
        else:
            contract_identifier_hex = response["result"][1]["tr_receipt"]["log"][0]["address"]
        if not self.validator.is_hex(contract_identifier_hex):
            lcc.log_error("Wrong format of address, got {}".format(contract_identifier_hex))
            raise Exception("Wrong format of address")
        contract_id = "{}{}".format(self.get_object_type(self.echo.config.object_types.CONTRACT),
                                    int(str(contract_identifier_hex)[2:], 16))
        if not self.validator.is_contract_id(contract_id):
            lcc.log_error("Wrong format of contract id, got {}".format(contract_id))
            raise Exception("Wrong format of contract id")
        if new_contract:
            lcc.log_info("New Echo contract created, contract_id='{}'".format(contract_id))
        return contract_id

    def get_contract_output(self, response, output_type=None, in_hex=False, len_output_string=0, debug_mode=False):
        contract_output = str(response["result"][1].get("exec_res").get("output"))
        if debug_mode:
            lcc.log_debug("Output is '{}'".format(str(contract_output)))
        if in_hex:
            return contract_output
        if output_type == str:
            contract_output = (contract_output[128:])[:len_output_string * 2]
            return str(codecs.decode(contract_output, "hex").decode('utf-8'))
        if output_type == int:
            return int(contract_output, 16)
        if output_type == "contract_address":
            contract_id = "{}{}".format(self.get_object_type(self.echo.config.object_types.CONTRACT),
                                        int(str(contract_output[contract_output.find("1") + 1:]), 16))
            return contract_id

    @staticmethod
    def get_contract_log_data(response, output_type, log_format=None, debug_mode=False):
        if debug_mode:
            lcc.log_info("Logs are '{}'".format(json.dumps(response, indent=4)))
        if log_format:
            contract_logs = response
        else:
            contract_logs = response["result"][1].get("tr_receipt").get("log")
        if not contract_logs:
            raise Exception("Empty log")
        if len(contract_logs) == 1:
            contract_log_data = str(contract_logs.get("data"))
            if output_type == str:
                log_data = (contract_log_data[128:])[:int(contract_log_data[127]) * 2]
                return str(codecs.decode(log_data, "hex").decode('utf-8'))
            if output_type == int:
                return int(contract_log_data, 16)
        contract_log_data = []
        for i, log_data in enumerate(contract_logs):
            if output_type[i] == str:
                log_data = (log_data.get("data")[128:])[:int(log_data.get("data")[127]) * 2]
                contract_log_data.append(str(codecs.decode(log_data, "hex").decode('utf-8')))
            if output_type[i] == int:
                contract_log_data.append(int(log_data.get("data"), 16))
        return contract_log_data

    @staticmethod
    def get_account_details_template(account_name, private_key, public_key, brain_key):
        return {account_name: {"id": "", "private_key": private_key, "public_key": public_key, "brain_key": brain_key}}

    def generate_keys(self):
        brain_key_object = self.echo.brain_key()
        brain_key = brain_key_object.brain_key
        private_key_base58 = brain_key_object.get_private_key_base58()
        public_key_base58 = brain_key_object.get_public_key_base58()
        return [private_key_base58, public_key_base58, brain_key]

    def store_new_account(self, account_name):
        keys = self.generate_keys()
        account_details = self.get_account_details_template(account_name, keys[0], keys[1], keys[2])
        if not os.path.exists(WALLETS):
            with open(WALLETS, "w") as file:
                file.write(json.dumps(account_details))
            return keys[1]
        with open(WALLETS, "r") as file:
            data = json.load(file)
            data.update(account_details)
            with open(WALLETS, "w") as new_file:
                new_file.write(json.dumps(data))
        return keys[1]

    def get_account_by_name(self, account_name, database_api_identifier, debug_mode=False):
        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        database_api_identifier, debug_mode=debug_mode)
        response = self.get_response(response_id, debug_mode=debug_mode)
        if response.get("error"):
            lcc.log_error("Error received, response:\n{}".format(response))
            raise Exception("Error received")
        return response

    def register_account(self, account_name, registration_api_identifier, database_api_identifier, debug_mode=False):
        public_key = self.store_new_account(account_name)
        self.__id += 1
        callback = self.__id
        account_params = [callback, account_name, public_key, public_key]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        registration_api_identifier, debug_mode=debug_mode)
        response = self.get_response(response_id, debug_mode=debug_mode)
        if response.get("error"):
            lcc.log_error(
                "Account '{}' not registered, response:\n{}".format(account_name, json.dumps(response, indent=4)))
            raise Exception("Account not registered.")
        self.get_notice(callback, log_response=debug_mode, debug_mode=debug_mode)
        response = self.get_account_by_name(account_name, database_api_identifier, debug_mode=debug_mode)
        account_id = response.get("result").get("id")
        with open(WALLETS, "r") as file:
            data = json.load(file)
            data[account_name].update({"id": account_id})
            with open(WALLETS, "w") as new_file:
                new_file.write(json.dumps(data))
        return response

    def get_or_register_an_account(self, account_name, database_api_identifier, registration_api_identifier,
                                   debug_mode=False):
        response = self.get_account_by_name(account_name, database_api_identifier, debug_mode=debug_mode)
        if response.get("result") is None and self.validator.is_account_name(account_name):
            response = self.register_account(account_name, registration_api_identifier, database_api_identifier,
                                             debug_mode=debug_mode)
        if debug_mode:
            lcc.log_debug("Account is {}".format(json.dumps(response, indent=4)))
        return response

    def get_account_id(self, account_name, database_api_identifier, registration_api_identifier, debug_mode=False):
        account = self.get_or_register_an_account(account_name, database_api_identifier, registration_api_identifier,
                                                  debug_mode=debug_mode)
        account_id = account.get("result").get("id")
        if debug_mode:
            lcc.log_debug("Account '{}' with id '{}'".format(account_name, account_id))
        return account_id

    def get_accounts_ids(self, account_name, account_count, database_api_identifier, registration_api_identifier):
        account_ids = []
        for i in range(account_count):
            account_ids.append(self.get_account_id(account_name + str(i), database_api_identifier,
                                                   registration_api_identifier))
        return account_ids

    def get_required_fee(self, operation, database_api_identifier, asset="1.3.0", debug_mode=False):
        response_id = self.send_request(self.get_request("get_required_fees", [[operation], asset]),
                                        database_api_identifier)
        response = self.get_response(response_id)
        if debug_mode:
            lcc.log_debug("Required fee:\n{}".format(json.dumps(response, indent=4)))
        if response.get("result")[0].get("fee"):
            return [response.get("result")[0].get("fee")]
        return response.get("result")

    def add_fee_to_operation(self, operation, database_api_identifier, fee_amount=None, fee_asset_id="1.3.0",
                             debug_mode=False):
        try:
            if fee_amount is None:
                fee = self.get_required_fee(operation, database_api_identifier, asset=fee_asset_id,
                                            debug_mode=debug_mode)
                operation[1].update({"fee": fee[0]})
                return fee
            operation[1]["fee"].update({"amount": fee_amount, "asset_id": fee_asset_id})
            return fee_amount
        except KeyError as key:
            lcc.log_error("Add fee: That key does not exist: '{}'".format(key))
        except IndexError as index:
            lcc.log_error("Add fee: This index does not exist: '{}'".format(index))

    def collect_operations(self, list_operations, database_api_identifier, fee_amount=None, fee_asset_id="1.3.0",
                           debug_mode=False):
        if debug_mode:
            lcc.log_debug("List operations:\n{}".format(json.dumps(list_operations, indent=4)))
        if type(list_operations) is list:
            list_operations = [list_operations.copy()]
        for i in range(len(list_operations)):
            self.add_fee_to_operation(list_operations[i], database_api_identifier, fee_amount, fee_asset_id, debug_mode)
        return list_operations

    def get_contract_result(self, broadcast_result, database_api_identifier, debug_mode=False):
        contract_result = self.get_operation_results_ids(broadcast_result)
        if len([contract_result]) != 1:
            lcc.log_error("Need one contract id, got:\n{}".format(contract_result))
            raise Exception("Need one contract id")
        if self.validator.is_erc20_object_id(contract_result):
            return contract_result
        if not self.validator.is_contract_result_id(contract_result):
            lcc.log_error("Wrong format of contract result id, got {}".format(contract_result))
            raise Exception("Wrong format of contract result id")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        database_api_identifier, debug_mode=debug_mode)
        return self.get_trx_completed_response(response_id, debug_mode=debug_mode)

    def get_next_maintenance_time(self, database_api_identifier):
        response_id = self.send_request(self.get_request("get_dynamic_global_properties"), database_api_identifier)
        next_maintenance_time = self.get_response(response_id)["result"]["next_maintenance_time"].split('T')[1]
        lcc.log_info("Next maintenance time: '{}' in global time".format(next_maintenance_time))
        return next_maintenance_time

    @staticmethod
    def convert_time_in_seconds(time_format, separator=":"):
        time_format = time_format.split(separator)
        time_in_seconds = (int(time_format[0]) * 3600 + int(time_format[1]) * 60 + int(time_format[2]))
        return time_in_seconds

    @staticmethod
    def get_waiting_time_till_maintenance(next_maintenance_time_in_sec, time_now_in_sec):
        if next_maintenance_time_in_sec > time_now_in_sec:
            return next_maintenance_time_in_sec - time_now_in_sec
        return BLOCK_RELEASE_INTERVAL

    def wait_for_next_maintenance(self, database_api_identifier, print_log=True):
        next_maintenance_time_in_sec = self.convert_time_in_seconds(
            self.get_next_maintenance_time(database_api_identifier))
        time_now_in_sec = self.convert_time_in_seconds(self.get_time(global_time=True))
        waiting_time = self.get_waiting_time_till_maintenance(next_maintenance_time_in_sec, time_now_in_sec)
        lcc.log_info("Waiting for maintenance... Time to wait: '{}' seconds".format(waiting_time))
        self.set_timeout_wait(seconds=waiting_time, print_log=print_log)
        lcc.log_info("Maintenance finished")

    @staticmethod
    def get_keccak_standard_value(value, digest_bits=256, encoding="utf-8", print_log=True):
        keccak_hash = keccak.new(digest_bits=digest_bits)
        keccak_hash.update(bytes(value, encoding=encoding))
        keccak_hash_in_hex = keccak_hash.hexdigest()
        if print_log:
            lcc.log_info("'{}' value in keccak '{}' standard is '{}'".format(value, digest_bits, keccak_hash_in_hex))
        return keccak_hash_in_hex

    @staticmethod
    def _login_status(response):
        # Check authorization status
        try:
            if not response["result"]:
                lcc.log_error("Login failed!")
                raise Exception("Login failed!")
            lcc.log_info("Login successful")
        except KeyError as key:
            lcc.log_error("This key does not exist: '{}'".format(key))

    def __login_echo(self):
        # Login to Echo
        lcc.set_step("Login to Echo")
        response_id = self.send_request(self.get_request("login", ["", ""]))
        response = self.get_response(response_id)
        self._login_status(response)

    def _connect_to_echopy_lib(self):
        # Create connection to echopy-lib
        lcc.set_step("Open connection to echopy-lib")
        self.echo.connect(url=BASE_URL, debug=DEBUG)
        if self.echo.api.ws.connection is None:
            lcc.log_error("Connection to echopy-lib not established")
            raise Exception("Connection to echopy-lib not established")
        lcc.log_info("Connection to echopy-lib successfully created")

    def _disconnect_to_echopy_lib(self):
        # Close connection to echopy-lib
        lcc.set_step("Close connection to echopy-lib")
        self.echo.disconnect()
        if self.echo.api.ws.connection is not None:
            lcc.log_error("Connection to echopy-lib not closed")
            raise Exception("Connection to echopy-lib not closed")
        lcc.log_info("Connection to echopy-lib closed")

    def _connect_to_ethereum(self):
        # Create connection to ethereum
        lcc.set_step("Open connection to ethereum")
        lcc.log_url(ETHEREUM_URL)
        self.web3 = Web3(Web3.HTTPProvider(ETHEREUM_URL))
        if self.web3.isConnected() is None or not self.web3.isConnected():
            lcc.log_error("Connection to ethereum not established")
            raise Exception("Connection to ethereum not established")
        lcc.log_info("Connection to ethereum successfully created")

    def perform_pre_deploy_setup(self, database_api_identifier):
        # Perform pre-deploy for run tests on the empty node
        self._connect_to_ethereum()
        self._connect_to_echopy_lib()
        lcc.set_step("Pre-deploy setup")
        lcc.log_info("Empty node. Start pre-deploy setup...")
        if os.path.exists(WALLETS):
            os.remove(WALLETS)
        if os.path.exists(EXECUTION_STATUS_PATH):
            os.remove(EXECUTION_STATUS_PATH)
        pre_deploy_echo(self, database_api_identifier, lcc)
        lcc.log_info("Pre-deploy setup completed successfully")
        self._disconnect_to_echopy_lib()

    def check_node_status(self):
        database_api_identifier = self.get_identifier("database")
        if not ROPSTEN:
            response_id = self.send_request(self.get_request("get_named_account_balances", ["nathan", []]),
                                            database_api_identifier)
            if not self.get_response(response_id)["result"]:
                return self.perform_pre_deploy_setup(database_api_identifier)
        response_id = self.send_request(self.get_request("get_account_by_name", [self.accounts[0]]),
                                        database_api_identifier)
        if not self.get_response(response_id)["result"]:
            return self.perform_pre_deploy_setup(database_api_identifier)

    def setup_suite(self):
        # Check status of connection
        lcc.set_step("Open connection")
        lcc.log_url(BASE_URL)
        self.ws = self.create_connection_to_echo()
        if self.ws.connected is None or not self.ws.connected:
            lcc.log_error("WebSocket connection not established")
            raise Exception("WebSocket connection not established")
        lcc.log_info("WebSocket connection successfully created")
        self.receiver = Receiver(web_socket=self.ws)
        self.__login_echo()
        self.check_node_status()

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.ws.close()
        if self.ws.connected:
            lcc.log_error("WebSocket connection not closed")
            raise Exception("WebSocket connection not closed")
        lcc.log_info("WebSocket connection closed")
