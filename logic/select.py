"""
select
======
This module queries DF with the BASIS, STATUS and MAILS queries respectively.
"""

# third party
import pandas as pd

# local
from logic.config import (
    DATA_PATH,
    MAILHIST_PATH,
    PARAM,
    BASIS,
    BETALING,
    STATUS,
    MAILS,
    BUITEN_ZEEF,
)
from logic.startup import today, MAIL_HISTORIE, MAIL_VORIGE
from logic.moedertabel import DF


# parameters
uitgesloten_opleidingen = PARAM.uitgesloten_opleidingen
besluit_ok = ['S', 'T']


# basis
basis = DF.query(BASIS, engine='python')


# zeef
status  = ' or '.join([f"({query})" for query in STATUS.values()])

mail_vti = (
    basis
    .query(BETALING['open'], engine='python')
    .query(status, engine='python')
)

for name, query in MAILS.items():
    selection = mail_vti.query(query, engine='python').studentnummer
    mail_vti[f'm_{name}'] = mail_vti.studentnummer.isin(selection)

cols = [col for col in mail_vti.columns if col.startswith('m_')]
mail_stud = (
    mail_vti
    .groupby('studentnummer')
    [cols].sum()
    .applymap(bool)
)


# buiten zeef
basis_betaald = basis.query(BETALING['betaald'], engine='python')
mail_vti_bz = pd.DataFrame(columns=basis_betaald.columns)

for name, query in BUITEN_ZEEF.items():
    selection = basis_betaald.query(query, engine='python')
    if not selection.empty:
        mail_vti_bz = mail_vti_bz.append(selection, sort=False)
    mail_vti_bz[f'm_{name}'] = (
        mail_vti_bz.studentnummer.isin(selection.studentnummer)
    )

cols = [col for col in mail_vti_bz.columns if col.startswith('m_')]
mail_stud_bz = (
    mail_vti_bz.query(status, engine='python')
    .groupby('studentnummer')
    [cols].sum()
    .applymap(bool)
)


# combine buiten zeef with zeef
mail_vti = mail_vti.append(mail_vti_bz, sort=False)
mail_stud = mail_stud.append(mail_stud_bz, sort=False).fillna(False)
cols_mailing = [col for col in mail_stud.columns if col.startswith('m_')]


# checks
geen_mail = list(mail_stud.loc[mail_stud.sum(axis=1) == 0].index)
meer_mail = list(mail_stud.loc[mail_stud.sum(axis=1) > 1].index)


# set mail
mail_stud = mail_stud.loc[~mail_stud.index.isin(geen_mail + meer_mail)]
mail_stud['mail'] = mail_stud.idxmax(axis=1)
mail_stud['datum'] = today
mail_stud = mail_stud[['mail', 'datum']]

if MAIL_VORIGE.empty:
    mail_stud['datum_vorig'] = pd.NA
else:
    mail_stud = mail_stud.merge(MAIL_VORIGE, on=['studentnummer', 'mail'], how='left')

mail_stud['delta'] = mail_stud.datum - mail_stud.datum_vorig
mail_stud.delta.fillna(pd.Timedelta(days=999), inplace=True)
delta = pd.Timedelta(days=14)

mail_stud = (
    mail_stud
    .query("delta > @delta", engine='python')
    .drop(['datum_vorig', 'delta'], axis=1)
)


# aggregates
view_mail_vti = (
    mail_vti.groupby('soort')[cols_mailing].sum().astype(int)
).rename(mapper=lambda x: x[2:], axis=1)

view_mail_stud = pd.DataFrame(index=cols_mailing, columns=['aantal'], data=0)
df_mail_agg = (
    mail_stud
    .groupby('mail').count()
    .rename(columns={'datum': 'aantal'})
)
view_mail_stud.update(df_mail_agg)
view_mail_stud.rename(mapper=lambda x: x[2:], axis=0, inplace=True)
view_mail_stud = view_mail_stud.astype(int)
view_mail_stud.loc['Totaal'] = view_mail_stud.sum()


# update mailhistorie
MAIL_HISTORIE = MAIL_HISTORIE.append(
    mail_stud, sort=False
)
MAIL_HISTORIE.to_pickle(MAILHIST_PATH, protocol=4)
