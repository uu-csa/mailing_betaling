from functools import partial
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
        mailhistorie = pd.read_csv(
            path,
            dtype={'maand': int, 'studentnummer': str,},
            parse_dates = ['datum'],
            infer_datetime_format=True,
        ).set_index(['maand', 'studentnummer'])

        # find previous mail
        mail_vorig = (
            mailhistorie
            .query(f"datum < '{pd.Timestamp.today().date()}'")
            .groupby(['maand', 'studentnummer', 'mail']).max()
            .rename(columns={'datum': 'datum_vorig'})
            .reset_index(level=2)
        )
    except FileNotFoundError:
        cols = ['maand', 'studentnummer', 'mail', 'datum']
        mailhistorie = (
            pd.DataFrame(columns=cols).set_index(['maand', 'studentnummer'])
        )
        mail_vorig = pd.DataFrame().rename_axis('studentnummer')
    mailhistorie.datum = pd.to_datetime(mailhistorie.datum)
    return mailhistorie, mail_vorig


def update_mailhistorie(path, mailhistorie, mailinglijst, maand, is_gemaild):
    """Update mailhistorie. Twee mogelijkheden volgens `is_gemaild`:
    - Voeg een bepaalde maand uit mailinglijst toe aan mailhistorie
    - Verwijder voor een bepaalde maand berichten uit mailhistorie met
    datum vandaag
    """
    if is_gemaild:
        addition = mailinglijst.xs(maand, drop_level=False)
        mailhistorie = mailhistorie.append(addition, sort=False)
    else:
        today = pd.to_datetime('today').date()
        query = f"~(maand == {maand} and datum == '{today}')"
        mailhistorie = mailhistorie.query(query)
    mailhistorie.to_csv(path)
    return None


############### MAILINGLIJST ###############


def get_basis(bron):
    return bron.query(BASIS)


def get_mailings_per_vti(basis):
    "Wijs mailing toe per vti op basis van zeef."
    # zeef
    status = ' or '.join(STATUS.values())
    output = basis.query(BETALING['open']).query(status)
    for mail, query in MAILS.items():
        studentnummers = output.query(query).studentnummer
        output[mail] = output.studentnummer.isin(studentnummers)

    # buiten zeef
    df = basis.query(BETALING['betaald'])
    for mail, query in BUITEN_ZEEF.items():
        rows = df.query(query)
        output = output.append(rows, sort=False)
        output[mail] = output.studentnummer.isin(rows.studentnummer)

    output.loc[:, [*MAILS, *BUITEN_ZEEF]].fillna(False, inplace=True)
    return output


def get_mailings_per_student(mailings_per_vti):
    "Vorm tabel met mailings per vti om naar tabel met mailings per student."
    cols = [*MAILS, *BUITEN_ZEEF]
    return mailings_per_vti.groupby(['maand', 'studentnummer'])[cols].any()


def get_geen_mail_ontvangen(mailings_per_student):
    "Maak een lijst met studentnummers aan wie geen mail is gekoppeld."
    geen_mail = mailings_per_student.astype(int).sum(axis=1) == 0
    return list(mailings_per_student.loc[geen_mail].index)


def get_te_veel_mail_ontvangen(mailings_per_student):
    "Maak een lijst met studentnummers aan wie meer dan één mail is gekoppeld."
    te_veel = mailings_per_student.astype(int).sum(axis=1) > 1
    return list(mailings_per_student.loc[te_veel].index)


def get_kandidaten_voor_mailing(mailings_per_student, fouten):
    """Maak lijst met kandidaten die voor een mailing in aanmerking komen door
    de studenten bij wie fouten zijn opgetreden uit de mailinglijst te
    verwijderen."""
    df = mailings_per_student
    uitsluiten = df.index.isin(fouten)
    return df.loc[~uitsluiten].assign(
        mail = df.idxmax(axis=1),
        datum = pd.to_datetime('today').normalize()
    )[['mail', 'datum']]


def get_mailinglijst(kandidaten_voor_mailing, mail_vorig, termijn=14):
    """Maak mailinglijst van de kandidatetenlijst door kandidaten uit
    de tabel te verwijderen die korter dan `termijn` dagen geleden dezelfde
    mail hebben ontvangen.
    """
    df = kandidaten_voor_mailing
    if mail_vorig.empty:
        df['datum_vorig'] = pd.NA
        df.datum_vorig = pd.to_datetime(df.datum_vorig)
    else:
        df = df.merge(
            mail_vorig,
            on=['maand', 'studentnummer', 'mail'],
            how='left',
        )
    df['delta'] = pd.to_datetime(df.datum) - df.datum_vorig
    df.delta.fillna(pd.Timedelta(days=999), inplace=True)
    delta = pd.Timedelta(days=termijn)
    return df.query("delta > @delta").drop(['datum_vorig', 'delta'], axis=1)


############### AGGREGATEN ###############


def get_totalen_per_soort_vti(mailings_per_vti):
    "Totaal aantal toegewezen mails per soort vti."
    types = {col:int for col in MAILS.keys()}
    return (
        mailings_per_vti.astype(types)
        .groupby('soort')[[*MAILS, *BUITEN_ZEEF]].sum()
    )


def get_totalen_per_mailing(mailinglijst, maand=None):
    "Totaal aantal toegewezen studenten per mail eventueel per `maand`."
    s = pd.Series(index=[*MAILS, *BUITEN_ZEEF], name='aantal')

    if maand is not None:
        if maand in mailinglijst.index:
            mailinglijst = mailinglijst.xs(maand)
        else:
            mailinglijst = pd.DataFrame(columns=['mail'])

    s.update(mailinglijst.mail.value_counts())
    s = s.fillna(0).astype(int)
    s.loc['Totaal'] = s.sum()
    return s


def get_maandoverzicht(mailhistorie):
    "Maak maandoverzicht van mailhistorie."
    start = pd.Timestamp(2020, 6, 1)
    end = pd.Timestamp(2021, 9, 1)
    period = pd.date_range(start, end, freq='w')

    output = pd.DataFrame(index=period, columns=[*MAILS, *BUITEN_ZEEF])
    if not mailhistorie.empty:
        values = (
            mailhistorie.resample('w', on='datum')
            .mail.value_counts().unstack()
        )
        output.update(values)
    output = output.fillna(0).astype(int).assign(
        maand = lambda x: x.index.month_name(locale='nl').str.lower(),
        week = lambda x: x.index.isocalendar().week,
    ).set_index(['maand', 'week']).T

    output.loc['Totaal'] = output.sum()
    output[('Totaal', '')] = output.sum(axis=1)
    return output.reindex([*MAILS, *BUITEN_ZEEF, 'Totaal'])


def get_copypasta(mailinglijst):
    """Maak kopierbare reeksen studentnummers per maand en mailing in
    mailinglijst."""
    try:
        copypasta = dict()
        for maand in [9,10,11,12,1,2,3,4,5,6,7,8]:
            mails = dict()
            for mail in MAILS.keys():
                prev_idx = 0
                batches = dict()
                if maand in mailinglijst.index.remove_unused_levels().levels[0]:
                    df = mailinglijst.xs(maand,level=0).query("mail == @mail")
                    for batch in range(ceil(len(df) / 500)):
                        idx = 500 * (batch + 1)
                        batches[batch] = ';'.join(df.index[prev_idx:idx])
                        prev_idx = idx
                mails[mail] = batches
            copypasta[maand] = mails
    except:
        copypasta = dict()
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

kandidaten_mailing = get_kandidaten_voor_mailing(mailings_per_student, fouten)
mailinglijst = get_mailinglijst(kandidaten_mailing, mail_vorig)
copypasta = get_copypasta(mailinglijst)

totalen_per_soort_vti = get_totalen_per_soort_vti(mailings_per_vti)
totalen_per_mailing = get_totalen_per_mailing(mailinglijst)

maandoverzicht = get_maandoverzicht(mailhistorie)
