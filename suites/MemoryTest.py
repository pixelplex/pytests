# -*- coding: utf-8 -*-

import lemoncheesecake.api as lcc

from common.base_test import BaseTest

SUITE = {
    "description": "Trying to find memory leaks"
}


@lcc.tags("memory_test")
@lcc.suite("Trying to find memory leaks")
class MemoryTest(BaseTest):

    def __init__(self):
        super().__init__()
        self.__api_identifier = None

    def setup_suite(self):
        super().setup_suite()
        self._connect_to_echopy_lib()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__api_identifier = self.get_identifier("database")

    def teardown_suite(self):
        self._disconnect_to_echopy_lib()
        super().teardown_suite()

    @lcc.test("The scenario trying to find memory leaks")
    def memory_scenario(self):
        nathan_id = "1.2.12"
        nathan_private_key = "5JkYKpRDWeY3DN4qjZRKpEfxCqmTX17fsBJhupE9DJVVmJoGh6C"
        contract_bytecode = "608060405234801561001057600080fd5b50610326806100206000396000f3fe608060405260043610610" \
                            "03b576000357c010000000000000000000000000000000000000000000000000000000090048063bf3a9b" \
                            "0c1461003d575b005b34801561004957600080fd5b50610052610094565b604051808273fffffffffffff" \
                            "fffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191" \
                            "505060405180910390f35b600061009e610123565b604051809103906000f0801580156100ba573d60008" \
                            "03e3d6000fd5b5090507f8860d70e5b00031c5eb44ff56b037b8497064bcf3929d191503df422d0718a7a" \
                            "81604051808273ffffffffffffffffffffffffffffffffffffffff1673fffffffffffffffffffffffffff" \
                            "fffffffffffff16815260200191505060405180910390a190565b6040516101c7806101348339019056fe" \
                            "608060405234801561001057600080fd5b50336000806101000a81548173fffffffffffffffffffffffff" \
                            "fffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550610167" \
                            "806100606000396000f3fe608060405260043610610046576000357c01000000000000000000000000000" \
                            "000000000000000000000000000009004806302d05d3f1461004b5780634f8a2b4e146100a2575b600080" \
                            "fd5b34801561005757600080fd5b506100606100ac565b604051808273ffffffffffffffffffffffffff" \
                            "ffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001915050604051809" \
                            "10390f35b6100aa6100d1565b005b6000809054906101000a900473ffffffffffffffffffffffffffffff" \
                            "ffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff" \
                            "1673ffffffffffffffffffffffffffffffffffffffff166108fc34908115029060405160006040518083" \
                            "0381858888f19350505050158015610138573d6000803e3d6000fd5b5056fea165627a7a72305820c85" \
                            "767631d2b22e5cb49acf7889faa2db46e2cc01ef6c66512dbbddccec9e6880029a165627a7a72305820" \
                            "8dd385f281e660f6a686bd46698893655fba32f86d88f0ca5e2ff431a14b19400029"
        contract_count = 5
        list_operations = []
        contract_ids = []
        contract_results = []
        deploy_contract_method = "bf3a9b0c"
        created_contract_ids = []

        print("\nStep #1: Create '{}' contracts that can create another contract".format(contract_count))
        for i in range(contract_count):
            operation = self.echo_ops.get_create_contract_operation(echo=self.echo, registrar=nathan_id,
                                                                    bytecode=contract_bytecode,
                                                                    signer=nathan_private_key)
            collected_operation = self.collect_operations(operation, self.__api_identifier)
            list_operations.append(collected_operation)
        broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=list_operations)
        operation_results = self.get_operation_results_ids(broadcast_result)
        print("\noperation_results: {}".format(operation_results))

        for operation_result in operation_results:
            response_id = self.send_request(self.get_request("get_contract_result", [operation_result[1]]),
                                            self.__api_identifier)
            contract_results.append(self.get_trx_completed_response(response_id))

        for contract_result in contract_results:
            contract_id = self.get_contract_id(contract_result)
            contract_ids.append(contract_id)
        print("\ncontract_ids: {}".format(contract_ids))

        print("\nStep #2: Get objects of {} created_contracts".format(contract_count))
        params = [contract_ids]
        response_id = self.send_request(self.get_request("get_objects", params), self.__api_identifier)
        print("\nResponse of get_objects #1:\n{}".format(self.get_response(response_id)))

        print("\nStep #3: Call 'deploy_contract' method of all '{}' created_contracts".format(contract_count))
        for contract_id in contract_ids:
            operation = self.echo_ops.get_call_contract_operation(echo=self.echo, registrar=nathan_id,
                                                                  bytecode=deploy_contract_method, callee=contract_id,
                                                                  signer=nathan_private_key)
            collected_operation = self.collect_operations(operation, self.__api_identifier)
            broadcast_result = self.echo_ops.broadcast(echo=self.echo, list_operations=collected_operation)
            contract_result = self.get_contract_result(broadcast_result, self.__api_identifier)
            created_contract_id = self.get_contract_output(contract_result, output_type="contract_address")
            created_contract_ids.append(created_contract_id)
        print("\ncontract_ids by calling contract: {}".format(contract_ids))

        print("\nStep #4: Get objects of {} created_contracts by calling contract".format(contract_count))
        params = [contract_ids]
        response_id = self.send_request(self.get_request("get_objects", params), self.__api_identifier)
        print("\nResponse of get_objects #2:\n{}".format(self.get_response(response_id)))
