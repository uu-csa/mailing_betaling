"""
init
====
This module initializes the tool by:

1. Loading `mail_historie.pkl` as `mail_historie`
2. Preparing `mail_vorige`
3. Updating updating `betaalmail` tables if today is not in `mail_historie`
4. Loading the sql statement from `s_sih`
5. Loading the base data
"""

# standard library
# import timeit
# start = timeit.default_timer()
import datetime as dt
from collections import namedtuple

# third party
import pandas as pd

# local
# from query.query import connect, run_query
# from query.definition import QueryDef
import logic
from logic.config import PARAM, DATA_PATH, MAILHIST_PATH


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

print(f"Running version: {logic.__version__}\n")

print(
"""HI! IT'S ME -- THE APPLICATION SERVING THE WEBPAGES.
IF YOU SHUT ME DOWN, NO OTHER PAGES WILL BE SERVED!
"""
)

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
    MAIL_HISTORIE = pd.read_pickle(MAILHIST_PATH)

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


# load tables
frames = [
    'inschrijfhistorie', # 's_sih'
    'aanvangsjaar',      # 's_opl'
    'stoplicht',         # 's_stop'
    'adres',             # 's_adr_nl'
    'ooa_aanmelding',    # 's_ooa_aan'
    'ooa_rubriek',
    'finstorno',         # 's_fin_storno'
    'fingroepen',        # 's_fin_grp'
]
DataSet = namedtuple('DataSet', [f for f in frames])

# OSIRIS QUERY
# dfs = DataSet(**{
#     f:QueryResult.read_pickle(f"monitor/{f}_{PARAM.jaar}").frame
#     for f in frames
# })


print(f"using file '{MAILHIST_PATH}'")


def sanity_check(path):
    if testfile.exists():
        print(f">>> file '{path.name}' found")
    else:
        print(f">>> file '{path.name}' not found")
        return False

    if testfile.suffix == '.pkl':
        df = pd.read_pickle(testfile)
    else:
        df = pd.read_excel(testfile)

    last_record = df.mutatie_datum.max()
    print(f">>> last record was updated on {last_record}")

    if last_record < today:
        print(f">>> files are stale (expecting: {today})")
        return False

    print(">>> yay! sanity check passed")
    return True


testfile = DATA_PATH / 'inschrijfhistorie.pkl'
if sanity_check(testfile):
    dfs = DataSet(**{
        f:pd.read_pickle(DATA_PATH / f"{f}.pkl") for f in frames})
else:
    print(">>> osiris_query data not found, looking for access data")
    testfile = DATA_PATH / 'inschrijfhistorie.xlsx'
    while not sanity_check(testfile):
        print("please update data using access...")
        user = input("press enter to continue (enter . to exit): ")
        if user == '.':
            raise KeyboardInterrupt("cancelled by user")
        if user == 'i':
            break

    if user == 'i':
        dfs = DataSet(**{
            f:pd.read_pickle(DATA_PATH / f"{f}.pkl") for f in frames})
    else:
        dfs = DataSet(**{
            f:pd.read_excel(DATA_PATH / f"{f}.excel") for f in frames})
