"""
config
======
This module contains:

- MAIN_PATH (location of tool)
- `load_ini` (function to load ini with configparser)
"""

import configparser
from pathlib import Path

MAIN_PATH = Path(__file__).resolve().parent.parent

def load_ini(filename):
    # load parameters
    ini_file = MAIN_PATH / filename
    ini = configparser.ConfigParser()
    ini.read(ini_file, encoding='utf-8')
    return ini
