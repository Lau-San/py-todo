import os
from flask import Flask, render_template, url_for, redirect, current_app


def create_app(test_config=None):
    app = Flask(
        __name__,                       # The name of module
        instance_relative_config=True   # Configuration files are relative to the instance folder.
    )

    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'pytodo.sqlite'),
    )

    # Load instance config or test config
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return redirect(url_for('tasks.index'))

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import tasks
    app.register_blueprint(tasks.bp)

    return app
