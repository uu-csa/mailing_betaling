from datetime import datetime
from functools import partial
from pathlib import Path

import markdown
from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    redirect,
    send_from_directory,
    url_for,
)

import betaalmail.config as config
import betaalmail.mail as mail
import betaalmail.tables as tables


__version__ = '1.2'
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


maanden = {
    'sep': 9,
    'okt': 10,
    'nov': 11,
    'dec': 12,
    'jan': 1,
    'feb': 2,
    'mrt': 3,
    'apr': 4,
    'mei': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8
}


@bp.context_processor
def inject():
    get_mailhistorie = partial(
        mail.get_mailhistorie,
        config.PATH_MAILHISTORIE,
    )
    get_totalen_per_maand = partial(
        mail.get_totalen_per_mailing,
        mail.mailinglijst,
    )
    get_alle_kandidaten = partial(
        mail.get_totalen_per_mailing,
        mail.kandidaten_mailing,
    )

    return dict(
        version                   = __version__,
        title                     = 'betaalmail | ',
        maanden                   = maanden,
        datum                     = datetime.today().date(),
        get_mailhistorie          = get_mailhistorie,
        bron                      = mail.bron,
        basis                     = mail.basis,
        mailings_per_vti          = mail.mailings_per_vti,
        mailings_per_student      = mail.mailings_per_student,
        geen_mail                 = mail.geen_mail,
        meer_mail                 = mail.meer_mail,
        mailinglijst              = mail.mailinglijst,
        copypasta                 = mail.copypasta,
        totalen_per_soort_vti     = mail.totalen_per_soort_vti,
        get_alle_kandidaten       = get_alle_kandidaten,
        get_totalen_per_maand     = get_totalen_per_maand,
        maandoverzicht            = mail.maandoverzicht,
        query_bron                = sql_bron.split('\n'),
        query_basis               = config.BASIS.split('and'),
        query_betaling            = config.BETALING,
        query_verzoek             = config.STATUS,
        query_mailing             = config.MAILS,
        query_buitenzeef          = config.BUITEN_ZEEF,
        params                    = config.PARAMETERS,
        changelog                 = chlog,
        create_stoplicht          = tables.create_stoplicht,
        create_studentkenmerken   = tables.create_studentkenmerken,
        create_inschrijfkenmerken = tables.create_inschrijfkenmerken,
        create_mailings           = tables.create_mailings,
        create_mailhistorie       = tables.create_mailhistorie,
    )


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/mailings', methods=['GET', 'POST'])
def mailings():
    maand = request.args.get('maand')
    if maand is None:
        maand = datetime.now().month
    if request.method == 'POST':
        month, is_gemaild = request.get_json()
        mail.update_mailhistorie(
            config.PATH_MAILHISTORIE,
            mail.mailhistorie,
            mail.mailinglijst,
            maanden[month],
            is_gemaild,
        )
        mail.mailhistorie, _ = mail.get_mailhistorie(config.PATH_MAILHISTORIE)
        return redirect(url_for('betaalmail.mailings'))
    return render_template(
        'pages/mailings.html',
        heading='mailings',
        maand=int(maand),
    )


@bp.route('/totaallijsten')
def totaallijsten():
    return render_template(
        'pages/totaallijsten.html',
        heading='totaallijsten',
    )


@bp.route('/queries')
def queries():
    return render_template(
        'pages/queries.html',
        heading='queries',
    )


@bp.route('/overzichten')
def overzichten():
    return render_template(
        'pages/overzichten.html',
        heading='overzichten',
    )


@bp.route('/debugger', methods=['GET', 'POST'])
def debugger():
    if request.method == 'POST':
        studentnummer = request.form['studentnummer']
        return render_template(
            'pages/debugger.html',
            heading='debugger',
            studentnummer=studentnummer,
        )
    return render_template(
        'pages/debugger.html',
        heading='debugger',
    )


@bp.route("/changelog")
def changelog():
    return render_template(
        'pages/changelog.html',
        heading='pages/changelog',
    )


@bp.route("/download")
def download():
    path = Path(current_app.instance_path) / 'output'
    mailing = request.args.get('mailing')
    maand = request.args.get('maand')

    if mailing is not None:
        file = f"{mailing}.xlsx"
        mail.mailinglijst.xs(int(maand)).query(
            "mail == @mailing"
        ).index.to_frame().to_excel(path / file, index=False)
        return send_from_directory(path, file, as_attachment=True)

    else:
        file = f"laatste_rappel_maand_{maand}.xlsx"
        mail.get_kandidaten_voor_mailing(
            mail.mailings_per_student,
            mail.fouten,
        ).xs(int(maand)).to_excel(path / file)
        return send_from_directory(path, file, as_attachment=True)
