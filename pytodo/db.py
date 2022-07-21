import os

import sqlite3
import psycopg2

import click
import flask
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Return a connection to the database."""
    if 'db' not in g:
        if os.environ['FLASK_ENV'] == 'development':
            g.db = psycopg2.connect(
                host='localhost',
                database='pytodo',
                user=os.environ['DB_USERNAME'],
                password=os.environ['DB_PASSWORD']
            )
        else:
            g.db = psycopg2.connect(
                os.environ['DATABASE_URL'],
                sslmode='require'
            )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create tables."""
    db = get_db()
    cur = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        # db.executescript(f.read().decode('utf8'))
        cur.execute(f.read().decode('utf8'))
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app: flask.Flask):
    # Tell Flask to call this function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # Add a command that can be called with the flask command.
    app.cli.add_command(init_db_command)
