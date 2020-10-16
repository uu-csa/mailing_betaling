"""
moedertabel
===========
This module creates DF as `DataFrame`.
DF contains the all active enrolment requests.
The selected features are used for selecting the mailing groups.
"""

# standard library
from functools import wraps

# third party
import pandas as pd

# local
# from query.results import QueryResult
from betaalmail.config import PARAM, DATA_PATH
from betaalmail.startup import today, dfs


def shape(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        df, *_ = args
        result = func(*args, **kwargs)
        print(f"{func.__name__:.>48}", result.shape)
        return result
    return wrapper


@shape
def set_aanvangsjaar(df):
    """
    Add `aanvangsjaar` from `dfs.opl` as column to `df` and fill empty values with current year.
    """

    df = df.merge(dfs.aanvangsjaar, how='left')
    # df['aanvangsjaar'].cat.add_categories(PARAM.jaar, inplace=True)
    # df['aanvangsjaar'] = df['aanvangsjaar'].fillna(PARAM.jaar)
    return df


@shape
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


@shape
def set_nl_adres(df):
    """
    Add `nl_adres` as column to `df` and fill value if `studentnummer` is present in `dfs.adr_nl`.
    """

    df['nl_adres'] = df['studentnummer'].isin(dfs.adres['studentnummer'])
    return df


@shape
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


@shape
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
        .query("groep not in @factuur and groep not in @niet_sepa")
        ['studentnummer']
        )

    # factuur
    df['factuur'] = df['studentnummer'].isin(
        dfs.fingroepen
        .query("groep in @factuur")
        ['studentnummer']
        )

    # elders
    df['niet_sepa'] = df['studentnummer'].isin(
        dfs.fingroepen
        .query("groep in @niet_sepa")
        ['studentnummer']
        )

    # storno
    df = df.merge(dfs.finstorno, on='studentnummer', how='left')
    return df


@shape
def set_ooa(df):
    """
    Add information on online application processes to `df`.
    """

    p = PARAM.ooa_aanm
    q = "proces in @p"
    cols = [
        'studentnummer',
        'opleiding',
        'proces',
        'datum_status',
        'statusbesluit',
    ]
    subset = ['studentnummer', 'opleiding']
    data = (ooa
        .query(q)
        [cols]
        .sort_values('datum_status', ascending=True)
        .drop_duplicates(subset=subset, keep='last')
        .drop(['proces', 'datum_status'], axis=1)
        .rename(columns={'statusbesluit': 'statusbesluit_ooa'})
    )
    return df.merge(data, how='left')


@shape
def set_dipw(df):
    p = PARAM.ooa_dipw
    q = "proces in @p"
    cols = [
        'studentnummer',
        'opleiding',
        'proces',
        'datum_status',
        'statusbesluit',
    ]
    subset = ['studentnummer', 'opleiding']
    data = (ooa
        .query(q)
        [cols]
        .sort_values('datum_status', ascending=True)
        .drop_duplicates(subset=subset, keep='last')
        .drop(['proces', 'datum_status'], axis=1)
        .rename(columns={'statusbesluit': 'statusbesluit_dipw'})
    )
    return df.merge(data, how='left')


@shape
def set_accform(df):
    p = PARAM.acceptatieform
    q = "proces in @p"
    cols = [
        'studentnummer',
        'opleiding',
        'proces',
        'datum_status',
        'status_aanbieding',
    ]
    subset = ['studentnummer', 'opleiding']
    data = (ooa
        .query(q)
        [cols]
        .sort_values('datum_status', ascending=True)
        .drop_duplicates(subset=subset, keep='last')
        .drop(['proces', 'datum_status'], axis=1)
        .rename(columns={'status_aanbieding': 'acceptatieform'})
    )
    return df.merge(data, how='left')


@shape
def set_vvr_isa(df):
    p = PARAM.isa_vvr
    q = "proces in @p"
    data = ooa.query(q).studentnummer
    df['isa_vvr_proces'] = df.studentnummer.isin(data)
    return df


@shape
def set_vvr_isa_to_csa(df):
    query = "proces == 'MVV/VVR BMS20' and rubriekstatus == 'F21'"
    studentnummers = (
        dfs.ooa_aanmelding.merge(
            dfs.ooa_rubriek.query(query)
        )
    ).studentnummer
    return df.assign(
        vvr_van_isa_naar_csa = df.studentnummer.isin(studentnummers)
    )


@shape
def set_vvr_csa_to_isa(df):
    query = "proces == 'CSA_I_VVR' and rubriekstatus == 'X'"
    studentnummers = (
        dfs.ooa_aanmelding.merge(
            dfs.ooa_rubriek.query(query)
        )
    ).studentnummer
    return df.assign(
        vvr_van_csa_naar_isa = df.studentnummer.isin(studentnummers)
    )


@shape
def set_ffill_betaalvorm(df):
    """
    Copy betaalvorm to all

    1. if inschrijvingstatus == 'G', remove betaalvorm
    2. sort betaalvorm so non-empty values come first
    3. forward will these values per student
    """

    df.loc[df.inschrijvingstatus == 'G', 'betaalvorm'] == pd.NA
    df = df.sort_values('betaalvorm', ascending=False)
    df.betaalvorm = df.groupby('studentnummer').betaalvorm.ffill()
    return df


# prepare ooa
ooa = dfs.ooa_aanmelding
ooa['statusbesluit'] = ooa['besluit'].astype(str)
ooa['statusbesluit'] = ooa['statusbesluit'].replace({'nan': pd.NA})
ooa['statusbesluit'] = ooa['statusbesluit'].fillna(ooa['status'])


# create DF
print('_' * 75)
print()
DF = (dfs.inschrijfhistorie
    .pipe(set_aanvangsjaar)
    .pipe(set_soort_vti)
    .pipe(set_nl_adres)
    .pipe(set_ooa)
    .pipe(set_dipw)
    .pipe(set_accform)
    .pipe(set_vvr_isa)
    .pipe(set_vvr_isa_to_csa)
    .pipe(set_vvr_csa_to_isa)
    .pipe(set_fin)
    .pipe(set_stoplicht)
    .pipe(set_ffill_betaalvorm)
)
DF.datum_vti = DF.datum_vti.dt.date
print('_' * 75)
