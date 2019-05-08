import timeit
start = timeit.default_timer()

import datetime as dt
import pickle

import pandas as pd
import src.query as qry
from src.querydef import QueryDef
from .read_param import PARAM


#parameters
parameters = {'collegejaar': str(PARAM.jaar)}
today = dt.date.today()


def update_tables():
    # connect to database
    cursor = qry.connect()

    # queries to run
    queries = [
        'b_sih',
        'b_opl',
        'b_stop',
        'b_adr_nl',
        'b_ooa_aan',
        'b_fin_storno',
        'b_fin_grp',
    ]

    # run queries
    for query in queries:
        qd = QueryDef(f"betaalmail/{query}", parameters=parameters)
        qry.query(
            qd.outfile,
            qd.sql,
            cursor=cursor,
            description = qd.description,
            qtype=qd.qtype,
            columns=qd.columns,
            dtypes=qd.dtypes,
            remove_duplicates=qd.remove_duplicates,
            )

    # stop timer and print runtime
    stop = timeit.default_timer()
    sec = stop - start
    print(f"\n{'=' * 80}\nTotal runtime: {sec} seconds.\n{'=' * 80}\n")

    return None

def get_sql(query):
    qd = QueryDef(f"betaalmail/{query}", parameters=parameters)
    return qd.sql


# load history
try:
    df_mail_historie = pd.read_pickle('output/mail_historie.pkl')

    # update tables or exclude today
    if not today in list(df_mail_historie['datum']):
        update_tables()
    else:
        df_mail_historie = df_mail_historie.query("datum < @today")

    # find previous mail
    df_mail_vorige = (
        df_mail_historie
        .groupby(['studentnummer', 'mail']).max()
        .rename(columns={'datum': 'datum_vorig'})
        .reset_index()
        )
except FileNotFoundError:
    update_tables()
    cols = ['studentnummer', 'mail', 'datum']
    df_mail_historie = pd.DataFrame(columns=cols)
    df_mail_vorige = pd.DataFrame()

if df_mail_vorige.empty:
    cols = ['studentnummer', 'mail', 'datum_vorig']
    df_mail_vorige = pd.DataFrame(columns=cols)

SQL = get_sql('b_sih')
