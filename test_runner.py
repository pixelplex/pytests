from echopy import Echo
import os
import time
import json


def get_head_block_num(echo_connection):
    return echo_connection.api.database.get_dynamic_global_properties()["head_block_number"]


def run(echo_connection):
    if get_head_block_num(echo_connection):
        os.system("lcc run --exit-error-on-failure || lcc report --failed")
    else:
        time.sleep(5)
        run(echo_connection)


RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")
if "BASE_URL" not in os.environ:
    BASE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
else:
    BASE_URL = os.environ["BASE_URL"]

echo = Echo()
echo.connect(BASE_URL)
run(echo)
