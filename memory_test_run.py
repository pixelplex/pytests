# -*- coding: utf-8 -*-
import os

from echopy import Echo

echo = Echo()
echo.connect("ws://127.0.0.1:56451/ws")
os.system("lcc run -a memory_test")
