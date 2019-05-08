import datetime as dt

import numpy as np
import pandas as pd

import src.query as qry
from .read_param import PARAM


# load tables
frames = [
    'b_sih',
    'b_opl',
    'b_stop',
    'b_adr_nl',
    'b_ooa_aan',
    'b_fin_storno',
    'b_fin_grp',
]
class DataSet:
    pass
dfs = DataSet()
for frame in frames:
    setattr(
        dfs, frame[2:], qry.load_frame(f"betaalmail/{frame}_var_{PARAM.jaar}")
        )


def set_aanvangsjaar(df):
    # aanvangsjaar
    df = df.merge(dfs.opl, on=['sinh_id'], how='left')
    df['aanvangsjaar'].cat.add_categories(PARAM.jaar, inplace=True)
    df['aanvangsjaar'] = df['aanvangsjaar'].fillna(PARAM.jaar)
    return df

def set_soort_vti(df):
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
    df.loc[filt4, 'soort'] = 'edumod'
    df.loc[filt1 & filt5, 'soort'] = 'fixus'
    df.loc[filt1 & filt6, 'soort'] = 'selectie'
    df.loc[filt1 & df['soort'].isnull(), 'soort'] = 'matching'
    return df

def set_nl_adres(df):
    # nl adres
    df['nl_adres'] = df['studentnummer'].isin(dfs.adr_nl['studentnummer'])
    return df

def set_stoplicht(df):
    # stoplichtkleuren
    df_stop_kleur = dfs.stop.pivot(
        index='sinh_id',
        columns='criterium',
        values='kleur',
        ).astype('category').reset_index()
    df_stop_kleur.columns = [
        f"k_{column.lower()}"
        if column != 'sinh_id'
        else 'sinh_id'
        for column in df_stop_kleur.columns
        ]
    # stoplicht toelichting
    df_stop_toel = dfs.stop.pivot(
        index='sinh_id',
        columns='criterium',
        values='toelichting'
        ).astype('category').reset_index()
    df_stop_toel.columns = [
        column.lower()
        if column != 'sinh_id'
        else 'sinh_id'
        for column in df_stop_toel.columns
        ]

    df = df.merge(df_stop_kleur, on='sinh_id')
    df = df.merge(df_stop_toel, on='sinh_id')
    return df

def set_fin(df):
    factuur = PARAM.factuur

    # fingroepen
    df['fingroep'] = df['studentnummer'].isin(
        dfs.fin_grp
        .query("groep != @factuur")
        ['studentnummer']
        )

    # factuur
    df['factuur'] = df['studentnummer'].isin(
        dfs.fin_grp
        .query("groep == @factuur")
        ['studentnummer']
        )

    # storno
    df = df.merge(dfs.fin_storno, on='studentnummer', how='left')
    return df

def set_ooa(df):
    # aanmeldprocessen
    dfs.ooa_aan['statusbesluit'] = dfs.ooa_aan['besluit'].astype('str')
    dfs.ooa_aan['statusbesluit'] = dfs.ooa_aan['statusbesluit'].replace(
        to_replace={'nan': np.nan}
        )
    dfs.ooa_aan['statusbesluit'] = dfs.ooa_aan['statusbesluit'].fillna(
        dfs.ooa_aan['status']
        )

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
    df_ooa = (
        dfs.ooa_aan
        .query(q)[cols]
        .sort_values('datum_status', ascending=True)
        )

    cols = ['studentnummer', 'proces', 'opleiding']
    df_ooa = df_ooa.drop_duplicates(subset=cols, keep='last')
    df_ooa = df_ooa.rename(columns={'statusbesluit': 'statusbesluit_ooa'})

    cols = ['studentnummer', 'opleiding', 'statusbesluit_ooa']
    df = df.merge(df_ooa[cols], on=['studentnummer', 'opleiding'], how='left')

    ## ooa_diplomawaardering
    p = PARAM.ooa_dipw
    q = "proces in @p"
    cols = ['studentnummer', 'opleiding', 'statusbesluit']
    df_ooa = dfs.ooa_aan.query(q)[cols]
    df_ooa = df_ooa.rename(columns={'statusbesluit': 'statusbesluit_dipw'})
    df = df.merge(df_ooa, on=['studentnummer', 'opleiding'], how='left')

    ## acceptatieformulier master
    p = PARAM.acceptatieform
    q = "proces in @p"
    cols = ['studentnummer', 'opleiding', 'status_aanbieding']
    df_ooa = dfs.ooa_aan.query(q)[cols]
    df_ooa = df_ooa.rename(columns={'status_aanbieding': 'acceptatieform'})
    df = df.merge(df_ooa, on=['studentnummer', 'opleiding'], how='left')

    ## isa_vvr
    p = PARAM.isa_vvr
    q = "proces in @p"
    df_ooa = dfs.ooa_aan.query(q)['studentnummer']
    df['isa_vvr_proces'] = df['studentnummer'].isin(df_ooa)
    return df


# create DF
DF = set_aanvangsjaar(dfs.sih)
DF = set_soort_vti(DF)
DF = set_nl_adres(DF)
DF = set_ooa(DF)
DF = set_fin(DF)
DF = set_stoplicht(DF)
