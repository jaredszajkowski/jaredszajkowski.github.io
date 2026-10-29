```python
#######################################
## Import Libraries
#######################################

import sys

## Make sure the src folder is in the path
sys.path.insert(1, "./src/")

import re
import shutil
import subprocess
import time
import yaml

from colorama import Fore, Style, init
from datetime import datetime
from os import environ, getcwd, path
from pathlib import Path

# Code from lines 29-75 referenced from the UChicago
# FINM 32900 - Full-Stack Quantitative Finance course
# Credit to Jeremy Bejarano
# https://github.com/jmbejara

## Custom reporter: Print PyDoit Text in Green
# This is helpful because some tasks write to sterr and pollute the output in
# the console. I don't want to mute this output, because this can sometimes
# cause issues when, for example, LaTeX hangs on an error and requires
# presses on the keyboard before continuing. However, I want to be able
# to easily see the task lines printed by PyDoit. I want them to stand out
# from among all the other lines printed to the console.

from doit.reporter import ConsoleReporter
from settings import config
```