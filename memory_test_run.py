# -*- coding: utf-8 -*-
import os
import json
from echopy import Echo
from project import RESOURCES_DIR
if "BASE_URL" not in os.environ:
    BASE_URL = json.load(open(os.path.join(RESOURCES_DIR, "urls.json")))["BASE_URL"]
else:
    BASE_URL = os.environ["BASE_URL"]

echo = Echo()
echo.connect(BASE_URL)
os.system("lcc run -a memory_test")
