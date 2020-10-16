from math import ceil
from collections import namedtuple

# third party
import markdown
import pandas as pd
from flask import Blueprint, render_template, send_from_directory, request

# local
import betaalmail
from betaalmail import select
from betaalmail.config import HERE_PATH, PARAM
from betaalmail.startup import SQL
from betaalmail.views import (
    create_stoplicht,
    create_studentkenmerken,
    create_inschrijfkenmerken,
    create_overview,
)

bp = Blueprint('betaalmail', __name__, url_prefix='/betaalmail')


# parameters
## sidebar
items = dict(
    date        = select.today,
    last_update = select.DF.mutatie_datum.max(),
    sum_total   = len(select.MAIL_HISTORIE),
    n_bron      = len(select.DF),
    n_basis     = len(select.basis),
    n_vti       = len(select.mail_vti),
    n_stud      = len(select.mail_stud),
    geen_mail   = select.geen_mail,
    meer_mail   = select.meer_mail,
    version     = betaalmail.__version__,
)
SB = namedtuple('sidebar', items.keys())
sidebar = SB(**items)

## queries
items = dict(
    bron        = SQL.split('\n'),
    basis       = select.BASIS.split('and'),
    betaling    = select.BETALING,
    verzoek     = select.STATUS,
    mailing     = select.MAILS,
    buitenzeef  = select.BUITEN_ZEEF,
)
Q = namedtuple('queries', items.keys())
used_queries = Q(**items)


## tables
df = select.view_mail_stud.drop('Totaal')
df.index = [f'm_{idx}' for idx in df.index]
mails = df['aantal'].to_dict()

select.view_mail_vti.index.name = None
table_vti = select.view_mail_vti.to_html(border=0)
table_stud = select.view_mail_stud.to_html(border=0)

table_totals = create_overview(select.MAIL_HISTORIE, mails)


## changelog
with bp.open_resource('changelog.md', 'r') as f:
    changelog_md = markdown.markdown(f.read())


# copypasta
df = select.mail_stud
copypasta = dict()
for mail in mails:
    prev_idx = 0
    batches = dict()
    df_mail = df.query("mail == @mail")
    for batch in range(ceil(len(df_mail) / 500)):
        idx = 500 * (batch + 1)
        batches[batch] = ';'.join(df_mail.index[prev_idx:idx])
        prev_idx = idx
    copypasta[mail] = batches


# configure bp
title = 'betaalmail | '


@bp.route('/')
@bp.route('/mailings')
def mailings():
    return render_template(
        'mailings.html',
        title=title,
        heading='mailings',
        sidebar=sidebar,
        mails=mails,
        copypasta=copypasta,
    )


@bp.route('/queries')
def queries():
    return render_template(
        'queries.html',
        title=title,
        heading='queries',
        sidebar=sidebar,
        queries=used_queries,
        params=PARAM._asdict(),
    )


@bp.route('/results')
def results():
    return render_template(
        'results.html',
        title=title,
        heading='results',
        sidebar=sidebar,
        table_vti=table_vti,
        table_stud=table_stud,
        table_totals=table_totals,
    )


@bp.route('/debug', methods=['GET', 'POST'])
def debug():
    if request.method == 'POST':
        studentnummer = request.form['studentnummer']

        if select.DF.studentnummer.isin([studentnummer]).any():
            kenmerken = (
                f"<div class='flex wide'>"
                    f"<div class='flex column'>"
                        f"<h3>Kenmerken</h3>"
                        f"{create_studentkenmerken(select.DF, studentnummer)}"
                    f"</div>"
                    f"<div class='flex column'>"
                        f"<h3>Inschrijfregel</h3>"
                        f"{create_inschrijfkenmerken(select.DF, studentnummer)}"
                    f"</div>"
                    f"<div class='flex column'>"
                        f"<h3>Stoplicht</h3>"
                        f"{create_stoplicht(select.DF, studentnummer)}"
                    f"</div>"
                f"</div>"
            )
        else:
            kenmerken = (
                "<div class='flex wide'>studentnummer niet gevonden</div>"
            )

        try:
            mailhist = (
                select.MAIL_HISTORIE
                .loc[[studentnummer]]
                .to_html(border=0, index=False)
            )
        except KeyError:
            mailhist = "<i>geen</i>"

        try:
            gemaild = (
                select.mail_vti
                .set_index('studentnummer')[select.cols_mailing]
                .loc[[studentnummer]]
                .T
                .fillna(False)
                .to_html(border=0)
            )
        except KeyError:
            gemaild = "<i>geen</i>"

        datasets = {
            'bron':    select.DF.studentnummer.array,
            'basis':   select.basis.studentnummer.array,
            'verzoek': select.mail_vti.studentnummer.array,
            'mailing': select.mail_stud.index.array,
        }
        table = "<table><thead><th></th><th>aanwezig</th></thead><tbody>"
        for key, array in datasets.items():
            table += (
                "<tr>"
                f"<th>{key}</th>"
                f"<td>{studentnummer in array}</td>"
                "</tr>"
            )
        table += "</tbody></table>"
        result = (
            f"{kenmerken}"
            f"<hr>"
            f"<div class='flex wide'>"
                f"<div class='flex column'>"
                    f"<h3>Zeef</h3>"
                    f"{table}"
                f"</div>"
                f"<div class='flex column'>"
                    f"<h3>Mailings</h3>"
                    f"{gemaild}"
                f"</div>"
                f"<div class='flex column'>"
                    f"<h3>Mailhistorie</h3>"
                    f"{mailhist}"
                f"</div>"
            f"</div>"
        )
        return render_template(
            'debug.html',
            title=title,
            heading='debug',
            sidebar=sidebar,
            result=result,
        )
    return render_template(
        'debug.html',
        title=title,
        heading='debug',
        sidebar=sidebar,
    )


@bp.route("/changelog")
def changelog():
    return render_template(
        'changelog.html',
        title=title,
        heading='changelog',
        sidebar=sidebar,
        changelog=changelog_md,
    )


@bp.route("/download")
def download():
    file = request.args.get('f')
    df.query(
        "mail == @file"
    ).index.to_frame().to_excel(
        HERE_PATH / 'output' / f'{file}.xlsx',
        index=False,
    )
    path = HERE_PATH / 'output'
    return send_from_directory(
        path,
        f'{file}.xlsx',
        as_attachment=True,
    )
