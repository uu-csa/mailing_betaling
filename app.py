# standard library
import sys
sys.path.insert(0, '../osiris_query')

import threading
import webbrowser
from math import ceil

# third party
import pandas as pd
from flask import Flask, render_template, send_from_directory, jsonify, request

# local
import logic.select as select
from logic.config import MAIN_PATH
from logic.init import SQL


# parameters
date = select.today

sum_total = len(select.df_mail_historie)
n_bron = len(select.DF)
n_basis = len(select.df_basis)
n_vti = len(select.df_mail_vti)
n_stud = len(select.df_mail_stud)

query_bron = SQL.split('\n')
query_basis = select.BASIS.split('and')
query_verzoek = select.STATUS
query_mailing = select.MAILS

df = select.df_view_mail_stud.drop('Totaal')
df.index = [f'm_{idx}' for idx in df.index]
mail_names = df['aantal'].to_dict()

table_vti = select.df_view_mail_vti.to_html()
table_stud = select.df_view_mail_stud.to_html()
geen_mail = select.studenten_geen_mail
meer_mail = select.studenten_meer_mail

# copypasta
df = select.df_mail_stud
copypasta = dict()
for mail in mail_names:
    prev_idx = 0
    batches = dict()
    df_mail = df.query("mail == @mail")
    for batch in range(ceil(len(df_mail) / 500)):
        idx = 500 * (batch + 1)
        batches[batch] = ' '.join(df_mail['studentnummer'][prev_idx:idx])
        prev_idx = idx
    copypasta[mail] = batches

# configure app
app = Flask(__name__)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/')
def index():
    return render_template(
        'index.html',
        title='Dashboard Betaalmail',
        date=date,
        sum_total=sum_total,
        nbron=n_bron,
        nbasis=n_basis,
        nvti=n_vti,
        nstud=n_stud,
        query_bron=query_bron,
        query_basis=query_basis,
        query_verzoek=query_verzoek,
        query_mailing=query_mailing,
        mail_names=mail_names,
        copypasta=copypasta,
        table_vti=table_vti,
        table_stud=table_stud,
        geen_mail=geen_mail,
        meer_mail=meer_mail,
        )

@app.route("/download")
def download():
    file = request.args.get('f')
    df.query(
        "mail == @file"
        )['studentnummer'].to_excel(
            MAIN_PATH / 'output' / f'{file}.xlsx',
            index=False
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
    url = 'http://127.0.0.1:5000/'
    threading.Timer(4, lambda: webbrowser.open(url, new=2)).start()
    app.run(debug=False)
