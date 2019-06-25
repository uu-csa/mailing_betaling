"""
read_param
==========
This module reads `parameters.ini` and stores the results as `namedtuple`
in PARAM.
"""

import configparser
from collections import namedtuple
from .config import load_ini


def get_list(param):
    return param.strip('\n').split('\n')

# load parameters
ini = load_ini('parameters.ini')

# create namedtuple
param_names = [p for section in ini for p in ini[section]]
Parameters = namedtuple('Parameters', param_names)

# set parameters
values = list()
values.append(int(ini['parameters']['jaar']))
values.append(ini['parameters']['factuur'])

for parameter in ini['opleiding']:
    lst = get_list(ini['opleiding'][parameter])
    values.append(lst)

for parameter in ini['aanmelding']:
    lst = get_list(ini['aanmelding'][parameter])
    values.append(lst)

PARAM = Parameters._make(values)
