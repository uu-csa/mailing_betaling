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
import json
from pathlib import Path
from collections import namedtuple


HERE_PATH = Path(__file__).resolve().parent.parent


def load_ini(filename):
    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')
    return config


def get_string(item):
    return item.strip('"\n').replace('\n', ' ')

def get_path(item):
    return Path(get_string(item))


# CONFIG
cfg = load_ini(HERE_PATH / 'config.ini')
PATH_MOEDERTABEL = get_path(cfg['config']['moedertabel'])
PATH_MAILHISTORIE = get_path(cfg['config']['mailhistorie'])
PATH_PARAMETERS = get_path(cfg['config']['parameters'])
PATH_QUERIES = get_path(cfg['config']['queries'])


# PARAMETERS
with open(PATH_PARAMETERS, 'r', encoding='utf8') as f:
    PARAMETERS = json.load(f)


# QUERIES
qry = load_ini(PATH_QUERIES)
BASIS       = get_string(qry['basis']['basis'])
BETALING    = {k:get_string(v) for k,v in qry['betaling'].items()}
STATUS      = {k:get_string(v) for k,v in qry['status'].items()}
MAILS       = {k:get_string(v) for k,v in qry['mails'].items()}
BUITEN_ZEEF = {k:get_string(v) for k,v in qry['buiten_zeef'].items()}
