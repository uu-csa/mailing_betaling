"""
config
======
This module contains:

- HERE_PATH (location of tool)
- `load_ini` (function to load ini with configparser)

This module first reads `config.ini` and uses the DATA_PATH to read the
other configuration files: `parameters.ini` and `queries.ini`. The following
variables are stored:

Config
------
- DATA_PATH:     Path for the data
- MAILHIST_PATH: Path for history file

Parameters
----------
- PARAM:         Tuple with all parameter settings

Queries
-------
- BASIS:         Main selection
- BETALING:      Selection on digital authorization
- STATUS:        Selection based on enrolment requests
- MAILS:         Selection per student
- BUITEN_ZEEF:   Selection for exceptions

These are formatted to be used in the `query` method of a `DataFrame`.
"""

import configparser
from pathlib import Path
from collections import namedtuple


HERE_PATH = Path(__file__).resolve().parent.parent


def load_ini(filename):
    # load parameters
    ini_file = filename
    ini = configparser.ConfigParser()
    ini.read(ini_file, encoding='utf-8')
    return ini


def get_string(item):
    return item.strip('\n').replace('\n', ' ')


def to_list(item):
    return item.strip('\n').split('\n')


# CONFIG
cfg = load_ini(HERE_PATH / 'config.ini')
pathstring_data = cfg['config']['data']
if pathstring_data.startswith('.'):
    DATA_PATH = HERE_PATH / pathstring_data
else:
    DATA_PATH = Path(pathstring_data)

MAILHIST_PATH = DATA_PATH / cfg['config']['mailhistorie']


# PARAMETERS
par = load_ini(DATA_PATH / 'parameters.ini')
parameters = {k:to_list(v) for sect in par.values() for k,v in sect.items()}
Parameters = namedtuple('Parameters', parameters.keys())
PARAM = Parameters(**parameters)
PARAM = PARAM._replace(jaar=int(PARAM.jaar[0]))


# QUERIES
qry = load_ini(DATA_PATH / 'queries.ini')
BASIS       = get_string(qry['basis']['basis'])
BETALING    = {k:get_string(v) for k,v in qry['betaling'].items()}
STATUS      = {k:get_string(v) for k,v in qry['status'].items()}
MAILS       = {k:get_string(v) for k,v in qry['mails'].items()}
BUITEN_ZEEF = {k:get_string(v) for k,v in qry['buiten_zeef'].items()}
