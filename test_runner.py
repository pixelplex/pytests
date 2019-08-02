# -*- coding: utf-8 -*-
import json
import os
import sys
import time

from echopy import Echo

from project import RESOURCES_DIR, BLOCK_RELEASE_INTERVAL

if "BASE_URL" not in os.environ:
    BASE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
else:
    BASE_URL = os.environ["BASE_URL"]


def get_head_block_num(echo_connection):
    return echo_connection.api.database.get_dynamic_global_properties()["head_block_number"]


def run(echo_connection):
    if get_head_block_num(echo_connection):
        execution_status = os.system("if ! lcc run --exit-error-on-failure; then lcc report --failed; exit 1; fi")
        sys.exit(1 if execution_status > 1 else execution_status)
    else:
        time.sleep(BLOCK_RELEASE_INTERVAL)
        run(echo_connection)


echo = Echo()
echo.connect(BASE_URL)
run(echo)
