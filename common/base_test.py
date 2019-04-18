# -*- coding: utf-8 -*-
import codecs
import json
import os
import time

from echopy import Echo
from echopy.echobase import BrainKey
from lemoncheesecake.matching import is_str, is_integer, check_that_entry
from websocket import create_connection

import lemoncheesecake.api as lcc

from common.echo_operation import EchoOperations
from common.receiver import Receiver
from common.utils import Utils
from common.validation import Validator

from project import RESOURCES_DIR, BASE_URL, ECHO_CONTRACTS, WALLETS


class BaseTest(object):

    def __init__(self):
        super().__init__()
        self.ws = None
        self.receiver = None
        self.echo = Echo()
        self.utils = Utils()
        self.echo_ops = EchoOperations()
        self.__id = 0
        self.validator = Validator()
        self.echo_asset = "1.3.0"
        self.eeth_asset = "1.3.9"
        self.echo_acc1 = "echo-acc1"
        self.echo_acc2 = "echo-acc2"
        self.echo_acc3 = "echo-acc3"

    @staticmethod
    def create_connection_to_echo():
        return create_connection(url=BASE_URL)

    def check_uint64_numbers(self, response, key, quiet=False):
        if type(response.get(key)) is str:
            self.validator.is_uint64(response.get(key))
            check_that_entry(key, is_str(), quiet=quiet)
        else:
            check_that_entry(key, is_integer(), quiet=quiet)

    @staticmethod
    def set_timeout_wait(seconds):
        print("\nBefore sleep: {}".format(time.ctime()))
        time.sleep(seconds)
        print("\nAfter sleep: {}".format(time.ctime()))

    @staticmethod
    def get_value_for_sorting_func(str_value):
        return int(str_value[str_value.rfind('.') + 1:])

    @staticmethod
    def get_byte_code(variable_name):
        return ECHO_CONTRACTS[variable_name]

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
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

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
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

    def get_notice(self, id_response, object_id=None, log_block_id=True, log_response=False, debug_mode=False):
        # Receive notice from server
        try:
            if debug_mode:
                lcc.log_debug("Parameters: object_id={}, log_block_id={}".format(object_id, log_block_id))
                response = json.loads(self.ws.recv())
                lcc.log_debug("Received:\n{}".format(json.dumps(response, indent=4)))
                return response
            return self.receiver.get_notice(id_response, object_id, log_block_id, log_response)
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

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
        return operation_results[1]

    def get_contract_id(self, response, log_response=True):
        contract_identifier_hex = response["result"][1].get("exec_res").get("new_address")
        contract_id = "1.14.{}".format(int(str(contract_identifier_hex)[2:], 16))
        if log_response:
            lcc.log_info("Contract identifier is {}".format(contract_id))
        if not self.validator.is_contract_id(contract_id):
            lcc.log_error("Wrong format of contract id, got {}".format(contract_id))
            raise Exception("Wrong format of contract id")
        return contract_id

    @staticmethod
    def get_transfer_id(response, log_response=True):
        transfer_identifier_hex = str(response["result"][1].get("tr_receipt").get("log")[0].get("data"))[:64][-8:]
        transfer_id = int(str(transfer_identifier_hex), 16)
        if log_response:
            lcc.log_info("Transfer identifier is {}".format(transfer_id))
        return transfer_id

    @staticmethod
    def get_contract_output(response, in_hex=False):
        if in_hex:
            contract_output = str(response["result"][1].get("exec_res").get("output"))
            return contract_output
        contract_output = str(
            codecs.decode(str(response["result"][1].get("exec_res").get("output")), "hex").decode('utf-8'))
        return contract_output.replace("\u0000", "").replace("\u000e", "")

    @staticmethod
    def get_account_details_template(account_name, private_key, public_key, echorand_key):
        return {account_name: {"id": "", "private_key": private_key, "public_key": public_key,
                               "echorand_key": echorand_key}}

    @staticmethod
    def generate_keys():
        brain_key = BrainKey()
        private_key = str(brain_key.get_private_key())
        public_key = str(brain_key.get_public_key())
        echorand_key = str(brain_key.get_echorand_key())
        return [private_key, public_key, echorand_key]

    def store_new_account(self, account_name):
        keys = self.generate_keys()
        private_key = str(keys[0])
        public_key = str(keys[1])
        echorand_key = str(keys[2])
        account_details = self.get_account_details_template(account_name, private_key, public_key, echorand_key)
        if not os.path.exists(WALLETS):
            with open(WALLETS, "w") as file:
                file.write(json.dumps(account_details))
            return [public_key, echorand_key]
        with open(WALLETS, "r") as file:
            data = json.load(file)
            data.update(account_details)
            with open(WALLETS, "w") as new_file:
                new_file.write(json.dumps(data))
        return [public_key, echorand_key]

    def get_account_by_name(self, account_name, database_api_identifier, debug_mode=False):
        response_id = self.send_request(self.get_request("get_account_by_name", [account_name]),
                                        database_api_identifier, debug_mode=debug_mode)
        response = self.get_response(response_id, debug_mode=debug_mode)
        if response.get("error"):
            lcc.log_error("Error received, response:\n{}".format(response))
            raise Exception("Error received")
        return response

    def register_account(self, account_name, registration_api_identifier, database_api_identifier, debug_mode=False):
        public_data = self.store_new_account(account_name)
        self.__id += 1
        callback = self.__id
        account_params = [callback, account_name, public_data[0], public_data[0], public_data[0], public_data[1]]
        response_id = self.send_request(self.get_request("register_account", account_params),
                                        registration_api_identifier, debug_mode=debug_mode)
        response = self.get_response(response_id, debug_mode=debug_mode)
        if response.get("error"):
            lcc.log_error(
                "Account '{}' not registered, response:\n{}".format(account_name, json.dumps(response, indent=4)))
            raise Exception("Account not registered.")
        self.get_notice(response_id, debug_mode=debug_mode)
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
        except KeyError:
            lcc.log_error("That key does not exist!")
        except IndexError:
            lcc.log_error("This index does not exist!")

    def collect_operations(self, list_operations, database_api_identifier, fee_amount=None, fee_asset_id="1.3.0",
                           debug_mode=False):
        if debug_mode:
            lcc.log_debug("List operations:\n{}".format(json.dumps(list_operations, indent=4)))
        if type(list_operations) is list:
            list_operations = [list_operations]
        for i in range(len(list_operations)):
            self.add_fee_to_operation(list_operations[i], database_api_identifier, fee_amount, fee_asset_id)
        return list_operations

    def get_contract_result(self, broadcast_result, database_api_identifier, debug_mode=False):
        contract_result = self.get_operation_results_ids(broadcast_result)
        if len([contract_result]) != 1:
            lcc.log_error("Need one contract id, got:\n{}".format(contract_result))
            raise Exception("Need one contract id")
        if not self.validator.is_contract_result_id(contract_result):
            lcc.log_error("Wrong format of contract result id, got {}".format(contract_result))
            raise Exception("Wrong format of contract result id")
        response_id = self.send_request(self.get_request("get_contract_result", [contract_result]),
                                        database_api_identifier, debug_mode=debug_mode)
        return self.get_trx_completed_response(response_id, debug_mode=debug_mode)

    @staticmethod
    def _login_status(response):
        # Check authorization status
        try:
            if not response["result"]:
                lcc.log_error("Login failed!")
                raise Exception("Login failed!")
            lcc.log_info("Login successful")
        except KeyError:
            lcc.log_error("This key does not exist!")

    def __login_echo(self):
        # Login to Echo
        lcc.set_step("Login to Echo")
        response_id = self.send_request(self.get_request("login", ["", ""]))
        response = self.get_response(response_id)
        self._login_status(response)

    def _connect_to_echopy_lib(self):
        lcc.set_step("Open connection to echopy-lib")
        self.echo.connect(url=BASE_URL)
        if self.echo.api.ws.connection is None:
            lcc.log_error("Connection to echopy-lib not established")
            raise Exception("Connection to echopy-lib not established")
        lcc.log_info("Connection to echopy-lib successfully created")

    def _disconnect_to_echopy_lib(self):
        lcc.set_step("Close connection to echopy-lib")
        self.echo.disconnect()
        if self.echo.api.ws.connection is not None:
            lcc.log_error("Connection to echopy-lib not closed")
            raise Exception("Connection to echopy-lib not closed")
        lcc.log_info("Connection to echopy-lib closed")

    def setup_suite(self):
        # Check status of connection
        lcc.set_step("Open connection")
        lcc.log_url(BASE_URL)
        self.ws = self.create_connection_to_echo()
        if not self.ws.connected:
            lcc.log_error("WebSocket connection not established")
            raise Exception("WebSocket connection not established")
        lcc.log_info("WebSocket connection successfully created")
        self.receiver = Receiver(web_socket=self.ws)
        self.__login_echo()

    def teardown_suite(self):
        # Close connection to WebSocket
        lcc.set_step("Close connection")
        self.ws.close()
        if self.ws.connected:
            lcc.log_error("WebSocket connection not closed")
            raise Exception("WebSocket connection not closed")
        lcc.log_info("WebSocket connection closed")
