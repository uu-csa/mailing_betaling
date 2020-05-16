"""
moedertabel
===========
This module creates DF as `DataFrame`.
DF contains the all active enrolment requests.
The selected features are used for selecting the mailing groups.
"""

# standard library
import datetime as dt
from collections import namedtuple

# third party
import pandas as pd

# local
# from query.results import QueryResult
from logic.config import PARAM, MAIN_PATH, DATA_PATH
from logic.init import today


# load tables
frames = [
    'inschrijfhistorie', # 's_sih'
    'aanvangsjaar',      # 's_opl'
    'stoplicht',         # 's_stop'
    'adres',             # 's_adr_nl'
    'ooa_aanmelding',    # 's_ooa_aan'
    'finstorno',         # 's_fin_storno'
    'fingroepen',        # 's_fin_grp'
]
DataSet = namedtuple('DataSet', [f for f in frames])

# OSIRIS QUERY
# dfs = DataSet(**{
#     f:QueryResult.read_pickle(f"monitor/{f}_{PARAM.jaar}").frame
#     for f in frames
# })


def sanity_check(path):
    if testfile.exists():
        print(f">>> file '{path.name}' found")
        mdate = dt.datetime.fromtimestamp(testfile.stat().st_mtime).date()
    else:
        print(f">>> file '{path.name}' not found")
        return False

    print(f">>> files last updated on {mdate}")
    if mdate < today:
        print(f">>> files are stale (expecting: {today})")
        return False
    print(">>> sanity checked passed")
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


def set_aanvangsjaar(df):
    """
    Add `aanvangsjaar` from `dfs.opl` as column to `df` and fill empty values with current year.
    """

    df = df.merge(dfs.aanvangsjaar, how='left')
    # df['aanvangsjaar'].cat.add_categories(PARAM.jaar, inplace=True)
    # df['aanvangsjaar'] = df['aanvangsjaar'].fillna(PARAM.jaar)
    return df


def set_soort_vti(df):
    """
    Categorize enrollment requests and add categories to column `soort` in `df`.
    """

    # soort inschrijving
    filt1 = df['aanvangsjaar'] == PARAM.jaar
    filt2 = df['examentype'] == 'MA'
    filt3 = df['examentype'] == 'PM'
    filt4 = df['opleiding'].str.contains('-EB')
    filt5 = df['opleiding'].isin(PARAM.fixus)
    filt6 = df['opleiding'].isin(PARAM.selectie)

    df.loc[~filt1, 'soort'] = 'herinschrijving'
    df.loc[filt1 & filt2, 'soort'] = 'master'
    df.loc[filt1 & filt3, 'soort'] = 'premaster'
    df.loc[filt4, 'soort'] = 'educatief'
    df.loc[filt1 & filt5, 'soort'] = 'fixus'
    df.loc[filt1 & filt6, 'soort'] = 'selectie'
    df.loc[filt1 & df['soort'].isnull(), 'soort'] = 'matching'
    return df


def set_nl_adres(df):
    """
    Add `nl_adres` as column to `df` and fill value if `studentnummer` is present in `dfs.adr_nl`.
    """

    df['nl_adres'] = df['studentnummer'].isin(dfs.adres['studentnummer'])
    return df


def set_stoplicht(df):
    """
    Create `df_stop_kleur` and `df_stop_toel` through pivot from `dfs.stop`.
    Merge both tables with `df`.

    table           | columns                  | rows
    --------------- | ------------------------ | --------------------
    `kleuren`       | `stoplicht` colors       | enrollment requests
    `toelichting`   | `stoplicht` explanations | enrollment requests
    """

    stoplicht = [
        'identiteit_status',
        'verblijfsdocument',
        'vooropleiding_geverifieerd',
        'toelatingsbeschikking',
        'aanmelddeadline',
        'studiekeuzecheck',
        'plaatsingsbewijs',
        'verzilvering',
        'betaalwijze_bekend',
        'collegegeld_ineens_ontvangen',
        'machtiging',
        'bsa',
        'hogerejaars_geaccepteerd',
        'blokkade',
    ]

    # stoplichtkleuren
    kleuren = dfs.stoplicht.pivot(
        index='sinh_id',
        columns='criterium',
        values='kleur',
        ).astype('category').reset_index()
    kleuren.columns = [
        f"k_{column.lower()}"
        if column != 'sinh_id'
        else 'sinh_id'
        for column in kleuren.columns
    ]
    # stoplicht toelichting
    toelichting = dfs.stoplicht.pivot(
        index='sinh_id',
        columns='criterium',
        values='toelichting'
    ).astype('category').reset_index()
    toelichting.columns = [
        column.lower()
        if column != 'sinh_id'
        else 'sinh_id'
        for column in toelichting.columns
    ]

    df = df.merge(kleuren, how='left')
    df = df.merge(toelichting, how='left')
    for col in stoplicht:
        if col not in df.columns:
            df[col] = None
            df[f"k_{col}"] = None
    return df


def set_fin(df):
    """
    Add:
    - `fingroepen` (financial groups)
    - `factuur` (invoices)
    - `storno` (reversal information)
    as columns to `df`.
    """

    factuur   = PARAM.factuur
    niet_sepa = PARAM.niet_sepa

    # fingroepen
    df['fingroep'] = df['studentnummer'].isin(
        dfs.fingroepen
        .query("groep != @factuur and groep != @niet_sepa")
        ['studentnummer']
        )

    # factuur
    df['factuur'] = df['studentnummer'].isin(
        dfs.fingroepen
        .query("groep == @factuur")
        ['studentnummer']
        )

    # elders
    df['niet_sepa'] = df['studentnummer'].isin(
        dfs.fingroepen
        .query("groep == @niet_sepa")
        ['studentnummer']
        )

    # storno
    df = df.merge(dfs.finstorno, on='studentnummer', how='left')
    return df


def set_ooa(df):
    """
    Add information on online application processes to `df`.
    """

    ooa = dfs.ooa_aanmelding

    # aanmeldprocessen
    ooa['statusbesluit'] = ooa['besluit'].astype(str)
    ooa['statusbesluit'] = ooa['statusbesluit'].replace({'nan': pd.NA})
    ooa['statusbesluit'] = ooa['statusbesluit'].fillna(ooa['status'])

    ## ooa_aanmelding
    p = PARAM.ooa_aanm
    q = "proces in @p"
    cols = [
        'studentnummer',
        'opleiding',
        'proces',
        'datum_status',
        'statusbesluit',
    ]
    subset = ['studentnummer', 'proces', 'opleiding']
    data = (ooa
        .query(q)[cols].sort_values('datum_status', ascending=True)
        .drop_duplicates(subset=subset, keep='last')
        [['studentnummer', 'opleiding', 'statusbesluit']]
        .rename(columns={'statusbesluit': 'statusbesluit_ooa'})
    )
    df = df.merge(data, how='left')

    ## ooa_diplomawaardering
    p = PARAM.ooa_dipw
    q = "proces in @p"
    cols = ['studentnummer', 'opleiding', 'statusbesluit']
    data = (ooa
        .query(q)[cols]
        .rename(columns={'statusbesluit': 'statusbesluit_dipw'})
    )
    df = df.merge(data, how='left')

    ## acceptatieformulier master
    p = PARAM.acceptatieform
    q = "proces in @p"
    cols = ['studentnummer', 'opleiding', 'status_aanbieding']
    data = (ooa
        .query(q)[cols]
        .rename(columns={'status_aanbieding': 'acceptatieform'})
    )
    df = df.merge(data, how='left')

    ## isa_vvr
    p = PARAM.isa_vvr
    q = "proces in @p"
    data = ooa.query(q).studentnummer
    df['isa_vvr_proces'] = df.studentnummer.isin(data)
    return df


# create DF
DF = (dfs.inschrijfhistorie
    .pipe(set_aanvangsjaar)
    .pipe(set_soort_vti)
    .pipe(set_nl_adres)
    .pipe(set_ooa)
    .pipe(set_fin)
    .pipe(set_stoplicht)
)
DF.datum_vti = DF.datum_vti.dt.date
