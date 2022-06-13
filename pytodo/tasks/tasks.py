from flask import Blueprint, render_template, flash, g, request, redirect, url_for
from pytodo.auth import login_required
from pytodo.db import get_db

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@bp.route('/')
@login_required
def index():
    g.tasks = get_db().execute('SELECT * FROM task WHERE user_id = ?', (g.user['id'],)).fetchall()
    return render_template('tasks/tasks.html')


@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        task_desc = request.form['new_task_description']

        if task_desc != '':
            db = get_db()
            db.execute(
                'INSERT INTO task (user_id, description, done) VALUES (?, ?, ?)',
                (g.user['id'], task_desc, False))
            db.commit()

    return redirect(url_for('tasks.index'))


@bp.route('/complete')
@login_required
def complete():
    return 'Completing task'
