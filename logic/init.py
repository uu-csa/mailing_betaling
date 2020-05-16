"""
init
====
This module initializes the tool by:

1. Loading `mail_historie.pkl` as `mail_historie`
2. Preparing `mail_vorige`
3. Updating updating `betaalmail` tables if today is not in `mail_historie`
4. Loading the sql statement from `s_sih`
"""

# standard library
# import timeit
# start = timeit.default_timer()
import datetime as dt

# third party
import pandas as pd

# local
# from query.query import connect, run_query
# from query.definition import QueryDef
from logic.config import PARAM, MAIN_PATH, DATA_PATH


ascii = """
==========================================================================
    __           __                     __                        _     _
   / /_   ___   / /_  ____ _  ____ _   / /   ____ ___   ____ _   (_)   / /
  / __ \ / _ \ / __/ / __ `/ / __ `/  / /   / __ `__ \ / __ `/  / /   / /
 / /_/ //  __// /_  / /_/ / / /_/ /  / /   / / / / / // /_/ /  / /   / /
/_.___/ \___/ \__/  \__,_/  \__,_/  /_/   /_/ /_/ /_/ \__,_/  /_/   /_/

==========================================================================
"""
print(ascii)


#parameters
parameters = {'collegejaar': str(PARAM.jaar)}
today = dt.date.today()


# def update_tables():
#     # connect to database
#     cursor = connect()

#     # queries to run
#     queries = [
#         's_sih',
#         's_opl',
#         's_stop',
#         's_adr_nl',
#         's_ooa_aan',
#         's_fin_storno',
#         's_fin_grp',
#     ]

#     # run queries
#     for query in queries:
#         run_query(f"betaalmail/{query}", cursor=cursor, parameters=parameters)

#     # stop timer and print runtime
#     stop = timeit.default_timer()
#     sec = stop - start
#     print(f"\n{'=' * 80}\nTotal runtime: {sec} seconds.\n{'=' * 80}\n")

#     return None


# def get_sql(query):
#     qd = QueryDef.from_ini(name=f"monitor/{query}")
#     qd(parameters=parameters)
#     return qd.sql


# load history
try:
    file = MAIN_PATH / 'output/mail_historie.pkl'
    MAIL_HISTORIE = pd.read_pickle(file)

    # update tables or exclude today
    if not today in list(MAIL_HISTORIE.datum):
        # update_tables()
        pass
    else:
        MAIL_HISTORIE = MAIL_HISTORIE.query("datum < @today")

    # find previous mail
    MAIL_VORIGE = (
        MAIL_HISTORIE
        .groupby(['studentnummer', 'mail']).max()
        .rename(columns={'datum': 'datum_vorig'})
        .reset_index(level=1)
        )
except FileNotFoundError:
    # update_tables()
    cols = ['mail', 'datum']
    MAIL_HISTORIE = pd.DataFrame(columns=cols).rename_axis('studentnummer')
    MAIL_VORIGE = pd.DataFrame().rename_axis('studentnummer')


# SQL = get_sql('inschrijfhistorie')
with open(DATA_PATH / 'sql.txt', 'r') as f:
    SQL = f.read()
