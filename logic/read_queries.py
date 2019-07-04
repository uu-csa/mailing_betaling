"""
read_queries
============
This module reads `queries.ini` and stores the following variables as `string`:

- BASIS: Main selection
- STATUS: Selection based on enrolment requests
- MAILS: Selection per student

These are formatted to be used in the `query` method of a `DataFrame`.
"""

import configparser
from collections import namedtuple
from logic.config import load_ini


def get_string(query):
    return query.strip('\n').replace('\n', ' ')

# load queries
ini = load_ini('queries.ini')

# set queries
BASIS = get_string(ini['basis']['basis'])
STATUS = {query:get_string(ini['status'][query]) for query in ini['status']}
MAILS = {query:get_string(ini['mails'][query]) for query in ini['mails']}
BUITEN_ZEEF = {
    query:get_string(ini['buiten_zeef'][query]) for query in ini['buiten_zeef']
    }
