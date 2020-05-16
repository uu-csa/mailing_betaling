# standard library
# import sys
# sys.path.insert(0, '../osiris_query')

import threading
import webbrowser
from math import ceil
from collections import namedtuple

# third party
import pandas as pd
from flask import Flask, render_template, send_from_directory, request

# local
import logic.select as select
from logic.config import MAIN_PATH, PARAM
from logic.init import SQL
from logic.views import (
    create_stoplicht,
    create_studentkenmerken,
    create_inschrijfkenmerken,
    create_overview,
)

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
queries = Q(**items)


##tables
df = select.view_mail_stud.drop('Totaal')
df.index = [f'm_{idx}' for idx in df.index]
mails = df['aantal'].to_dict()

select.view_mail_vti.index.name = None
table_vti = select.view_mail_vti.to_html(border=0)
table_stud = select.view_mail_stud.to_html(border=0)

table_totals = create_overview(select.MAIL_HISTORIE, mails)


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


# configure app
app = Flask(__name__)
title = 'Dashboard | BETAALMAIL'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/')
@app.route('/mailings')
def view_mailings():
    return render_template(
        'mailings.html',
        title=title,
        heading='mailings',
        sidebar=sidebar,
        mails=mails,
        copypasta=copypasta,
    )


@app.route('/queries')
def view_queries():
    return render_template(
        'queries.html',
        title=title,
        heading='queries',
        sidebar=sidebar,
        queries=queries,
        params=PARAM._asdict(),
    )


@app.route('/results')
def view_results():
    return render_template(
        'results.html',
        title=title,
        heading='results',
        sidebar=sidebar,
        table_vti=table_vti,
        table_stud=table_stud,
        table_totals=table_totals,
    )


@app.route('/debug', methods=['GET', 'POST'])
def view_debug():
    if request.method == 'POST':
        studentnummer = request.form['studentnummer']
        try:
            mailhist = (
                select.MAIL_HISTORIE
                .loc[[studentnummer]]
                .to_html(border=0, index=False)
            )
        except KeyError:
            mailhist = "<i>geen</i>"

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
            f"<hr>"
            f"<div class='flex wide'>"
                f"<div class='flex column'>"
                    f"<h3>Mailhistorie</h3>"
                    f"{mailhist}"
                f"</div>"
                f"<div class='flex column'>"
                    f"<h3>Zeef</h3>"
                    f"{table}"
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


@app.route("/download")
def download():
    file = request.args.get('f')
    df.query(
        "mail == @file"
    ).index.to_frame().to_excel(
        MAIN_PATH / 'output' / f'{file}.xlsx',
        index=False,
    )
    path = MAIN_PATH / 'output'
    return send_from_directory(
        path,
        f'{file}.xlsx',
        as_attachment=True,
    )


@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':
    url = 'http://localhost:5555'
    threading.Timer(3, lambda: webbrowser.open(url, new=2)).start()
    app.run(debug=True, port=5555)
