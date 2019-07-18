# -*- coding: utf-8 -*-
import json
import os.path
import sys

from lemoncheesecake.project import SimpleProjectConfiguration, HasMetadataPolicy, HasPreRunHook, HasPostRunHook
from lemoncheesecake.validators import MetadataPolicy

project_dir = os.path.dirname(__file__)
sys.path.append(project_dir)

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")
GENESIS = json.load(open(os.path.join(os.path.dirname(__file__), "genesis.json")))

if "BASE_URL" not in os.environ:
    BASE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
else:
    BASE_URL = os.environ["BASE_URL"]

if "GANACHE_URL" not in os.environ:
    GANACHE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["GANACHE_URL"]
else:
    GANACHE_URL = os.environ["GANACHE_URL"]

if "NATHAN_PK" not in os.environ:
    NATHAN_PK = json.load(open(os.path.join(RESOURCES_DIR, "private_keys.json")))["NATHAN_PK"]
else:
    NATHAN_PK = os.environ["NATHAN_PK"]

if "INIT0_PK" not in os.environ:
    INIT0_PK = json.load(open(os.path.join(RESOURCES_DIR, "private_keys.json")))["INIT0_PK"]
else:
    INIT0_PK = os.environ["INIT0_PK"]

ECHO_OPERATIONS = json.load(open(os.path.join(RESOURCES_DIR, "echo_operations.json")))
ECHO_CONTRACTS = json.load(open(os.path.join(RESOURCES_DIR, "echo_contracts.json")))
WALLETS = os.path.join(RESOURCES_DIR, "wallets.json")
EXECUTION_STATUS_PATH = os.path.join(RESOURCES_DIR, "execution_status.json")
ECHO_INITIAL_BALANCE = int(GENESIS["initial_balances"][0]["amount"])
ECHO_ASSET_SYMBOL = GENESIS["initial_balances"][0]["asset_symbol"]
INITIAL_ACCOUNTS = GENESIS["initial_accounts"]
INITIAL_ACCOUNTS_COUNT = len(INITIAL_ACCOUNTS)
INITIAL_ACCOUNTS_NAMES = []
for i in range(INITIAL_ACCOUNTS_COUNT):
    INITIAL_ACCOUNTS_NAMES.append(INITIAL_ACCOUNTS[i]["name"])
INITIAL_ACCOUNTS_ETH_ADDRESSES = []
for i in range(INITIAL_ACCOUNTS_COUNT):
    if "eth_address" in INITIAL_ACCOUNTS[i]:
        INITIAL_ACCOUNTS_ETH_ADDRESSES.append(INITIAL_ACCOUNTS[i]["eth_address"])
ACCOUNT_PREFIX = "account"
DEFAULT_ACCOUNTS_COUNT = 1000
MAIN_TEST_ACCOUNT_COUNT = 1
BLOCK_RELEASE_INTERVAL = GENESIS["initial_parameters"]["block_interval"]
ETH_ASSET_SYMBOL = "EETH"
ETH_ASSET_ID = GENESIS["initial_parameters"]["sidechain_config"]["ETH_asset_id"]
ETH_CONTRACT_ADDRESS = "0x" + GENESIS["initial_parameters"]["sidechain_config"]["eth_contract_address"]
UNPAID_FEE_METHOD = "0x19c4518a"
COMMITTEE = "0x130f679d"

ETHEREUM_OPERATIONS = json.load(open(os.path.join(RESOURCES_DIR, "ethereum_transactions.json")))
ETHEREUM_CONTRACTS = json.load(open(os.path.join(RESOURCES_DIR, "ethereum_contracts.json")))
with open(".env") as env_file:
    ETH_PRIVATE_KEY = (env_file.readline().split('RPC_ACCOUNT=')[1]).split(",")[0]


class MyProjectConfiguration(SimpleProjectConfiguration, HasMetadataPolicy, HasPreRunHook, HasPostRunHook):

    def get_metadata_policy(self):
        policy = MetadataPolicy()
        policy.add_property_rule(
            "type", ("method", "operation", "scenario", "other"), required=False
        )
        policy.add_property_rule(
            "suite_run_option_1", "main", on_suite=True, required=False
        )
        policy.add_property_rule(
            "suite_run_option_2", "positive", on_suite=True, required=False
        )
        policy.add_property_rule(
            "suite_run_option_3", "negative", on_suite=True, required=False
        )
        return policy


project = MyProjectConfiguration(
    suites_dir=os.path.join(project_dir, "suites"),
    fixtures_dir=os.path.join(project_dir, "fixtures"),
    report_title="ECHO tests"
)
