import pandas as pd

from .config import MAIN_PATH
from .read_param import PARAM
from .read_queries import BASIS, STATUS, MAILS
from .init import today, df_mail_historie, df_mail_vorige
from .prep import DF


# parameters
geen_mail = PARAM.geen_mail
besluit_ok = ['S', 'T']

# zeef
df_basis = DF.query(BASIS, engine='python')
status = ' or '.join([f'({STATUS[query]})' for query in STATUS])
df_mail_vti = df_basis.query(status, engine='python').copy()

for query in MAILS:
    selection = df_mail_vti.query(
        MAILS[query],
        engine='python')['studentnummer']
    df_mail_vti[f'm_{query}'] = df_mail_vti['studentnummer'].isin(selection)

cols = ['studentnummer']
cols_mailing = [col for col in df_mail_vti.columns if col.startswith('m_')]
cols.extend(cols_mailing)
df_mail_stud = (
    df_mail_vti[cols]
    .groupby('studentnummer').sum()
    .applymap(bool)
    )

# checks
geen_mail = df_mail_stud.sum(axis=1) == 0
meer_mail = df_mail_stud.sum(axis=1) > 1

studenten_geen_mail = list(df_mail_stud.loc[geen_mail].index)
studenten_meer_mail = list(df_mail_stud.loc[meer_mail].index)

# set mail
df_mail_stud = df_mail_stud.loc[~geen_mail & ~meer_mail]
df_mail_stud['mail'] = df_mail_stud.idxmax(axis=1)
df_mail_stud['datum'] = today
df_mail_stud = df_mail_stud.drop(cols_mailing, axis=1).reset_index()
df_mail_stud = df_mail_stud.merge(
    df_mail_vorige,
    on=['studentnummer', 'mail'],
    how='left'
)
df_mail_stud['delta'] = df_mail_stud['datum'] - df_mail_stud['datum_vorig']
df_mail_stud['delta'].fillna(pd.Timedelta(days=999), inplace=True)

delta = pd.Timedelta(days=14)
df_mail_stud = (
    df_mail_stud
    .query("delta > @delta", engine='python')
    .drop(['datum_vorig', 'delta'], axis=1)
    )

# aggregates
df_view_mail_vti = (
    df_mail_vti.groupby('soort')[cols_mailing].sum().astype(int)
    ).rename(mapper=lambda x: x[2:], axis=1)
del df_view_mail_vti.index.name

df_view_mail_stud = pd.DataFrame(index=cols_mailing, columns=['aantal'], data=0)
df_mail_agg = (
    df_mail_stud
    .groupby('mail').count()
    .rename(columns={'studentnummer': 'aantal'})
    )
df_view_mail_stud.update(df_mail_agg)
df_view_mail_stud.rename(mapper=lambda x: x[2:], axis=0, inplace=True)
df_view_mail_stud = df_view_mail_stud.astype(int)
df_view_mail_stud.loc['Totaal'] = df_view_mail_stud.sum()

# update mailhistorie
df_mail_historie = df_mail_historie.append(
    df_mail_stud, ignore_index=True, sort=False
    )
df_mail_historie.to_pickle('output/mail_historie.pkl')
