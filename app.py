# standard library
import threading
import webbrowser
from pathlib import Path

import click
from flask import Flask, request, render_template


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho


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


    @app.route('/shutdown')
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'

    import betaalmail
    app.register_blueprint(betaalmail.bp)

    return app


app = create_app()


if __name__ == '__main__':
    url = 'http://localhost:1337/betaalmail/'
    threading.Timer(2.5, lambda: webbrowser.open(url, new=2)).start()
    app.run(debug=False, port=1337)
