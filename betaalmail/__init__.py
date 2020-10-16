__version__ = '1.04'
__license__ = 'GPLv3+'
__author__  = 'L.C. Vriend'
__email__   = 'l.c.vriend@uu.nl'


import os
from pathlib import Path
from flask import Flask, request, render_template


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True,
    )
    instance_path = Path(app.instance_path)
    print(instance_path)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    instance_path.mkdir(parents=True, exist_ok=True)


    @app.context_processor
    def inject_version():
        return dict(version=__version__)

    # a simple page that says hello
    # @app.route('/')
    # @app.route('/betaalmail')
    # def home():
    #     return render_template('mailings.html')

    @app.route('/shutdown')
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'

    from betaalmail import betaalmail
    app.register_blueprint(betaalmail.bp)

    return app
