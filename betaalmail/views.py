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


def create_stoplicht(df, id):
    return (
        df
        .set_index(['studentnummer', 'opleiding'])
        .loc[id, [f"k_{tup[1]}" for tup in stoplichtkleuren]]
        .T
        .astype(str)
        .fillna('')
        .set_index(pd.MultiIndex.from_tuples(stoplichtkleuren))
        .style
        .applymap(show_color)
    ).render()


studentkenmerken = [
    'nl_adres',
    'fingroep',
    'factuur',
    'niet_sepa',
    'betalingsachterstand',
    'isa_vvr_proces',
    'vvr_van_isa_naar_csa',
    'vvr_van_csa_naar_isa',
]


def create_studentkenmerken(df, id):
    return (
        df
        .drop_duplicates(subset='studentnummer')
        .set_index('studentnummer')
        .loc[[id], studentkenmerken]
        .fillna(False)
        .T
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
    'statusbesluit_dipw',
    'acceptatieform',
]


def create_inschrijfkenmerken(df, id):
    return (
        df
        .set_index(['studentnummer', 'opleiding'])
        .loc[id, inschrijving]
        .T
        .fillna('')
    ).to_html(border=0)


maanden = {
        1:  'jan',
        2:  'feb',
        3:  'maa',
        4:  'apr',
        5:  'mei',
        6:  'jun',
        7:  'jul',
        8:  'aug',
        9:  'sep',
        10: 'okt',
        11: 'nov',
        12: 'dec',
    }


def create_overview(df, cols):
    start = pd.Timestamp(2020, 5, 1)
    end = pd.Timestamp(2020, 10, 1)
    index = pd.date_range(start, end, freq='w')

    values = (
        df
        .astype({'datum': 'datetime64[ns]'})
        .set_index('datum')
        .resample('w')
        .mail
        .value_counts()
        .unstack()
    )

    data = pd.DataFrame(index=index, columns=cols)
    data.update(values)
    data['maand'] = data.index.month
    data.maand = data.maand.replace(maanden)
    data.index = data.index.week
    data.index.name = 'week'
    data = data.set_index('maand', append=True).swaplevel().T
    data.index = [item[2:] for item in data.index]
    data.loc['Totaal'] = data.sum()
    data[('Totaal', '')] = data.sum(axis=1).astype(int)
    return data.to_html(na_rep='', border=0)
