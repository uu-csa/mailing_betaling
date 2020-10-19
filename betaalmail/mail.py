from math import ceil

import pandas as pd

from betaalmail.config import (
    PATH_MAILHISTORIE,
    PATH_MOEDERTABEL,
    PARAMETERS,
    BASIS,
    BETALING,
    STATUS,
    MAILS,
    BUITEN_ZEEF,
)


############### MAILHISTORIE ###############


def get_mailhistorie(path):
    try:
        mailhistorie = pd.read_pickle(path)
        if pd.Timestamp.today().date() in mailhistorie.datum:
            mailhistorie = mailhistorie.query("datum < @today")

        # find previous mail
        mail_vorig = (
            mailhistorie
            .groupby(['studentnummer', 'mail']).max()
            .rename(columns={'datum': 'datum_vorig'})
            .reset_index(level=1)
        )
    except FileNotFoundError:
        cols = ['mail', 'datum']
        mailhistorie = pd.DataFrame(columns=cols).rename_axis('studentnummer')
        mail_vorig = pd.DataFrame().rename_axis('studentnummer')
    mailhistorie.datum = pd.to_datetime(mailhistorie.datum)
    return mailhistorie, mail_vorig


def set_mailhistorie(path, mailhistorie, mailinglijst):
    "Update mailhistorie."
    mailhistorie = mailhistorie.append(mailinglijst, sort=False)
    mailhistorie.to_pickle(path, protocol=4)
    return None


############### MAILINGLIJST ###############


def get_basis(df):
    return df.query(BASIS)


def get_mailings_per_vti(df):
    "Wijs mailing toe per vti op basis van zeef."
    # zeef
    status = ' or '.join(STATUS.values())
    output = df.query(BETALING['open']).query(status)
    for mail, query in MAILS.items():
        studentnummers = output.query(query).studentnummer
        output[mail] = output.studentnummer.isin(studentnummers)

    # buiten zeef
    df = df.query(BETALING['betaald'])
    for mail, query in BUITEN_ZEEF.items():
        rows = df.query(query)
        output = output.append(rows, sort=False)
        output[mail] = output.studentnummer.isin(rows.studentnummer)

    output[[*MAILS]].fillna(False, inplace=True)
    return output


def get_mailings_per_student(df):
    "Vorm tabel met mailings per vti om naar tabel met mailings per student."
    return df.groupby('studentnummer')[[*MAILS]].any()


def get_geen_mail_ontvangen(df):
    "Maak een lijst met studentnummers aan wie geen mail is gekoppeld."
    return list(df.loc[df.sum(axis=1) == 0].index)


def get_te_veel_mail_ontvangen(df):
    "Maak een lijst met studentnummers aan wie meer dan één mail is gekoppeld."
    return list(df.loc[df.sum(axis=1) > 1].index)


def get_mailinglijst(df, fouten, mail_vorige):
    """Maak mailinglijst van tabel met mailings per student door de volgende
    gevallen uit de tabel te verwijderen:

    1. Student heeft géén of meer dan één mail toegewezen gekregen.
    2. Student heeft korter dan twee weken geleden dezelfde mail ontvangen.
    """
    df = df.loc[~df.index.isin(fouten)].assign(
        mail = df.idxmax(axis=1),
        datum = pd.to_datetime('today')
    )[['mail', 'datum']]

    if mail_vorige.empty:
        df['datum_vorig'] = pd.NA
    else:
        df = df.merge(mail_vorige, on=['studentnummer', 'mail'], how='left')

    df['delta'] = df.datum - pd.to_datetime(df.datum_vorig)
    df.delta.fillna(pd.Timedelta(days=999), inplace=True)
    delta = pd.Timedelta(days=14)

    return df.query("delta > @delta").drop(['datum_vorig', 'delta'], axis=1)


############### AGGREGATEN ###############


def get_totalen_per_soort_vti(df):
    "Totaal aantal toegewezen mails per soort vti."
    types = {col:int for col in MAILS.keys()}
    return df.astype(types).groupby('soort')[[*MAILS]].sum()


def get_totalen_per_mailing(df):
    "Totaal aantal toegewezen studenten per mail."
    s = df.sum().rename('aantal')
    s.loc['Totaal'] = s.sum()
    return s


def get_maandoverzicht(df):
    "Maak maandoverzicht van mailhistorie."
    start = pd.Timestamp(2020, 5, 1)
    end = pd.Timestamp(2020, 10, 1)
    period = pd.date_range(start, end, freq='w')

    values = df.resample('w', on='datum').mail.value_counts().unstack()
    output = pd.DataFrame(index=period, columns=values.columns)
    output.update(values)
    output = output.fillna(0).astype(int).assign(
        maand = lambda x: x.index.month_name(locale='nl').str.lower(),
        week = lambda x: x.index.week,
    ).set_index(['maand', 'week']).T

    output.loc['Totaal'] = output.sum()
    output[('Totaal', '')] = output.sum(axis=1)
    return output


def get_copypasta(df):
    "Maak kopierbare reeksen studentnummers per mailing in mailinglijst."
    copypasta = dict()
    for mail in MAILS.keys():
        prev_idx = 0
        batches = dict()
        df_mail = df.query("mail == @mail")
        for batch in range(ceil(len(df_mail) / 500)):
            idx = 500 * (batch + 1)
            batches[batch] = ';'.join(df_mail.index[prev_idx:idx])
            prev_idx = idx
        copypasta[mail] = batches
    return copypasta


############### SCRIPT ###############


uitgesloten_opleidingen = PARAMETERS['opleiding']['geen_mail']
mailhistorie, mail_vorig = get_mailhistorie(PATH_MAILHISTORIE)

bron = pd.read_pickle(PATH_MOEDERTABEL)
basis = get_basis(bron)

mailings_per_vti = get_mailings_per_vti(basis)
mailings_per_student = get_mailings_per_student(mailings_per_vti)

geen_mail = get_geen_mail_ontvangen(mailings_per_student)
meer_mail = get_te_veel_mail_ontvangen(mailings_per_student)
fouten = geen_mail + meer_mail

mailinglijst = get_mailinglijst(mailings_per_student, fouten, mail_vorig)
copypasta = get_copypasta(mailinglijst)

totalen_per_soort_vti = get_totalen_per_soort_vti(mailings_per_vti)
totalen_per_mailing = get_totalen_per_mailing(mailings_per_student)
maandoverzicht = get_maandoverzicht(mailhistorie)
