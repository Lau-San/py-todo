import functools

import psycopg2.errors as db_errors

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import check_password_hash, generate_password_hash
from pytodo.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db = get_db()
                with db.cursor() as cur:
                    cur.execute(
                        'INSERT INTO users (username, password) VALUES (%s, %s);',
                        (username, generate_password_hash(password))
                    )
                    db.commit()
            except db_errors.UniqueViolation:
                error = f'{username} is already registered.'
            else:
                print(f'User {username} added to the database.')
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        with db.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE username = %s;', (username,))
            search = cur.fetchall()

        error = None

        if len(search) < 1:
            error = 'Incorrect username.'
            flash(error)
            return render_template('auth/login.html')

        user = search[0]

        if not check_password_hash(user[2], password):
            error = 'Incorrect password.'
            flash(error)
            return render_template('auth/login.html')

        session.clear()
        session['user_id'] = user[0]
        print(session['user_id'])
        return redirect(url_for('index'))

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        with db.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cur.fetchall()[0]
            g.user = {
                'id': user[0],
                'username': user[1]
            }


def login_required(view):
    @functools.wraps(view)
    def wrapper(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapper


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
