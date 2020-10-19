import pandas as pd


stoplichtkleuren = [
    ('personalia',   'identiteit_status'),
    ('personalia',   'verblijfsdocument'),
    ('personalia',   'vooropleiding_geverifieerd'),
    ('fixus',        'plaatsingsbewijs'),
    ('fixus',        'verzilvering'),
    ('matching',     'aanmelddeadline'),
    ('matching',     'studiekeuzecheck'),
    ('inschrijving', 'toelatingsbeschikking'),
    ('inschrijving', 'hogerejaars_geaccepteerd'),
    ('inschrijving', 'bsa'),
    ('inschrijving', 'blokkade'),
    ('betaling',     'betaalwijze_bekend'),
    ('betaling',     'machtiging'),
    ('betaling',     'collegegeld_ineens_ontvangen'),
]


def show_color(x):
    if x == 'GROEN':
        value = 'green'
    elif x == 'GEEL':
        value = 'yellow'
    elif x == 'ROOD':
        value = 'red'
    else:
        value = 'lightgray'
    return f"background-color: {value}; color: {value};"


def create_stoplicht(df, studentnummer):
    return (
        df.set_index(['studentnummer', 'opleiding'])
        .loc[studentnummer, [f"k_{tup[1]}" for tup in stoplichtkleuren]]
        .T.astype(str).fillna('')
        .set_index(pd.MultiIndex.from_tuples(stoplichtkleuren))
        .style.applymap(show_color)
    ).render()


studentkenmerken = [
    'adres_student_nl',
    'fingroep_aanwezig',
    'factuur',
    'niet_sepa',
    'betalingsachterstand',
    'proces_vvr_isa',
    'vvr_van_isa_naar_csa',
    'vvr_van_csa_naar_isa',
]


def create_studentkenmerken(df, studentnummer):
    return (
        df.drop_duplicates(subset='studentnummer')
        .set_index('studentnummer')
        .loc[[studentnummer], studentkenmerken].T
        # .fillna(False).T
    ).to_html(border=0)


inschrijving = [
    'soort',
    'datum_vti',
    'inschrijvingstatus',
    'actiefcode',
    'betaalvorm',
    'flex_deelname',
    'flex_aantal_ec',
    'statusbesluit_ooa',
    'statusbesluit_dipw_isa',
    'acceptatieform',
]


def create_inschrijfkenmerken(df, studentnummer):
    return (
        df.set_index(['studentnummer', 'opleiding'])
        .loc[studentnummer, inschrijving]
        .T.fillna('')
    ).to_html(border=0)


def create_mailhistorie(df, studentnummer):
    return (
        df.loc[[studentnummer]]
        .to_html(border=0, index=False)
    )


def create_mailings(df, studentnummer):
    return (
        df.set_index('studentnummer')[cols_mailing]
        .loc[[studentnummer]]
        .T.fillna(False)
        .to_html(border=0)
    )
