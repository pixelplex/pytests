# -*- coding: utf-8 -*-
import json
import os.path
import sys

from lemoncheesecake.project import SimpleProjectConfiguration, HasMetadataPolicy, HasPreRunHook, HasPostRunHook
from lemoncheesecake.validators import MetadataPolicy

project_dir = os.path.dirname(__file__)
sys.path.append(project_dir)

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")

if "BASE_URL" not in os.environ:
    BASE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
else:
    BASE_URL = os.environ["BASE_URL"]

ECHO_OPERATIONS = json.load(open(os.path.join(RESOURCES_DIR, "echo_operations.json")))
ECHO_CONTRACTS = json.load(open(os.path.join(RESOURCES_DIR, "echo_contracts.json")))
WALLETS = os.path.join(RESOURCES_DIR, "wallets.json")


class MyProjectConfiguration(SimpleProjectConfiguration, HasMetadataPolicy, HasPreRunHook, HasPostRunHook):

    def get_metadata_policy(self):
        policy = MetadataPolicy()
        policy.add_property_rule(
            "type", ("method", "operation", "scenario", "other"), required=False
        )
        policy.add_property_rule(
            "testing", ("main", "positive", "negative"), on_suite=True, required=False
        )
        return policy


project = MyProjectConfiguration(
    suites_dir=os.path.join(project_dir, "suites"),
    fixtures_dir=os.path.join(project_dir, "fixtures"),
    report_title="ECHO tests"
)
