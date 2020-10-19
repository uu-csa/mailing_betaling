from datetime import datetime

# third party
import markdown
from flask import Blueprint, render_template, send_from_directory, request

# local
import betaalmail.config as config
import betaalmail.mail as mail
import betaalmail.tables as tables
from betaalmail.tables import (
    create_stoplicht,
    create_studentkenmerken,
    create_inschrijfkenmerken,
)


__version__ = '1.1'
__license__ = 'GPLv3+'
__author__  = 'L.C. Vriend'
__email__   = 'l.c.vriend@uu.nl'


ascii = """
==========================================================================
    __           __                     __                        _     _
   / /_   ___   / /_  ____ _  ____ _   / /   ____ ___   ____ _   (_)   / /
  / __ \ / _ \ / __/ / __ `/ / __ `/  / /   / __ `__ \ / __ `/  / /   / /
 / /_/ //  __// /_  / /_/ / / /_/ /  / /   / / / / / // /_/ /  / /   / /
/_.___/ \___/ \__/  \__,_/  \__,_/  /_/   /_/ /_/ /_/ \__,_/  /_/   /_/

==========================================================================
"""
print(ascii)
print(f"Running version: {__version__}\n")


bp = Blueprint(
    'betaalmail',
    __name__,
    url_prefix='/betaalmail',
    template_folder='templates',
)


with bp.open_resource('content/changelog.md', 'r') as f:
    chlog = markdown.markdown(f.read())


with bp.open_resource('content/bron.sql', 'r') as f:
    sql_bron = f.read()


@bp.context_processor
def inject():
    return dict(
        version               = __version__,
        datum                 = datetime.today().date(),
        mailhistorie          = mail.mailhistorie,
        bron                  = mail.bron,
        basis                 = mail.basis,
        mailings_per_vti      = mail.mailings_per_vti,
        mailings_per_student  = mail.mailings_per_student,
        geen_mail             = mail.geen_mail,
        meer_mail             = mail.meer_mail,
        mailinglijst          = mail.mailinglijst,
        copypasta             = mail.copypasta,
        totalen_per_soort_vti = mail.totalen_per_soort_vti,
        totalen_per_mailing   = mail.totalen_per_mailing,
        maandoverzicht        = mail.maandoverzicht,
        query_bron            = sql_bron.split('\n'),
        query_basis           = config.BASIS.split('and'),
        query_betaling        = config.BETALING,
        query_verzoek         = config.STATUS,
        query_mailing         = config.MAILS,
        query_buitenzeef      = config.BUITEN_ZEEF,
        params                = config.PARAMETERS,
        changelog             = chlog,
        create_stoplicht          = tables.create_stoplicht,
        create_studentkenmerken   = tables.create_studentkenmerken,
        create_inschrijfkenmerken = tables.create_inschrijfkenmerken,
    )


# configure bp
title = 'betaalmail | '


@bp.route('/')
@bp.route('/mailings')
def mailings():
    return render_template(
        'pages/mailings.html',
        title=title,
        heading='mailings',
    )


@bp.route('/queries')
def queries():
    return render_template(
        'pages/queries.html',
        title=title,
        heading='queries',
    )


@bp.route('/results')
def results():
    return render_template(
        'pages/results.html',
        title=title,
        heading='results',
    )


@bp.route('/debug', methods=['GET', 'POST'])
def debug():
    if request.method == 'POST':
        studentnummer = request.form['studentnummer']

        return render_template(
            'pages/debug.html',
            title=title,
            heading='debug',
            studentnummer=studentnummer,
        )
    return render_template(
        'pages/debug.html',
        title=title,
        heading='debug',
    )


@bp.route("/changelog")
def changelog():
    return render_template(
        'pages/changelog.html',
        title=title,
        heading='pages/changelog',
    )


@bp.route("/download")
def download():
    file = request.args.get('f')
    mail_stud.query(
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
