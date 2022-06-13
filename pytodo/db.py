import sqlite3

import click
import flask
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Return a connection to the database."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create tables."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


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

# --------------------


# def connect(db: str):
#     con = sqlite3.connect(db)
#     cur = con.cursor()
#     return con, cur
#
#
# def add_task(desc: str):
#     """Add task to the database."""
#     con, cur = connect('task.db')
#     cur.execute('INSERT INTO tasks VALUES (?,?)', (desc, 'FALSE'))
#     con.commit()
#     con.close()
#
#
# def get_pending_tasks():
#     """Return a list of all tasks that are not done."""
#     con, cur = connect('task.db')
#     cur.execute('SELECT * FROM tasks')
#     print(cur.fetchall())
#     con.commit()
#     con.close()
