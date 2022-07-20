from flask import Blueprint, render_template, flash, g, request, redirect, url_for
from psycopg2.extras import DictCursor
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            '''
            SELECT
                id,
                description,
                done
            FROM tasks
            WHERE user_id = %s
            ''',
            (g.user['id'],)
        )
        tasks = cur.fetchall()

    # tasks = get_db().execute('SELECT * FROM task'
    #                          ' WHERE user_id = ?',
    #                          (g.user['id'],)).fetchall()

    todo = list(filter(lambda x: x['done'] == False, tasks))
    done = list(filter(lambda x: x['done'] == True, tasks))
    return render_template('tasks/tasks.html', tasks=tasks, todo=todo, done=done)


@bp.route('/create', methods=('POST',))
@login_required
def create():
    task_desc = request.form['description']

    if task_desc != '':
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                'INSERT INTO tasks (user_id, description, done) VALUES (%s, %s, %s)',
                (g.user['id'], task_desc, False))
            db.commit()

    return redirect(url_for('tasks.index'))


def get_task(id, check_user=True):
    with get_db().cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            'SELECT * FROM tasks WHERE id = %s',
            (id,)
        )

        task = cur.fetchone()

        if task is None:
            abort(404, f"Task id {id} doesn't exist.")

        if check_user and task['user_id'] != g.user['id']:
            abort(403)

    return task


@bp.route('/<int:id>/done', methods=('GET',))
@login_required
def done(id):
    get_task(id)

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            '''
            UPDATE tasks
            SET done = True
            WHERE id = %s
            ''',
            (id,)
        )
        db.commit()
    # db.execute('UPDATE task SET done = True'
    #            ' WHERE id = ?', (id,))
    # db.commit()
    return redirect(url_for('tasks.index'))


@bp.route('/<int:id>/undone', methods=('GET',))
@login_required
def undone(id):
    get_task(id)

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            '''
            UPDATE tasks
            SET done = False
            WHERE id = %s
            ''',
            (id,)
        )
        db.commit()
    # db.execute('UPDATE task SET done = False'
    #            ' WHERE id = ?', (id,))
    # db.commit()
    return redirect(url_for('tasks.index'))


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    get_task(id)

    db = get_db()
    with db.cursor() as cur:
        cur.execute('DELETE FROM tasks WHERE id = %s', (id,))
        db.commit()
    # db.execute('DELETE FROM task WHERE id = ?', (id,))
    # db.commit()
    return redirect(url_for('tasks.index'))
