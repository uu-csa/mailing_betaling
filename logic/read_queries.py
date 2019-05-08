import configparser
from collections import namedtuple
from .config import load_ini


def get_string(query):
    return query.strip('\n').replace('\n', ' ')

# load queries
ini = load_ini('queries.ini')

# set queries
BASIS = get_string(ini['basis']['basis'])
STATUS = {query:get_string(ini['status'][query]) for query in ini['status']}
MAILS = {query:get_string(ini['mails'][query]) for query in ini['mails']}
