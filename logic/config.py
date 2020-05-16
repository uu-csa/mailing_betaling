"""
config
======
This module contains:

- MAIN_PATH (location of tool)
- `load_ini` (function to load ini with configparser)
"""

import configparser
from pathlib import Path
from collections import namedtuple

MAIN_PATH = Path(__file__).resolve().parent.parent

def load_ini(filename):
    # load parameters
    ini_file = MAIN_PATH / filename
    ini = configparser.ConfigParser()
    ini.read(ini_file, encoding='utf-8')
    return ini

def get_list(param):
    return param.strip('\n').split('\n')

# load parameters
ini = load_ini('parameters.ini')

# create namedtuple
param_names = [p for section in ini for p in ini[section]]
Parameters = namedtuple('Parameters', param_names)

# set parameters
values = list()
values.append(ini['parameters']['data'])
values.append(int(ini['parameters']['jaar']))
values.append(ini['parameters']['factuur'])
values.append(ini['parameters']['niet_sepa'])

for parameter in ini['opleiding']:
    lst = get_list(ini['opleiding'][parameter])
    values.append(lst)

for parameter in ini['aanmelding']:
    lst = get_list(ini['aanmelding'][parameter])
    values.append(lst)

PARAM = Parameters._make(values)
DATA_PATH = MAIN_PATH / PARAM.data
