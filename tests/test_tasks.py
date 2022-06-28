import pytest
from flask import Flask, g
from flask.testing import FlaskClient, FlaskCliRunner
from werkzeug.test import TestResponse

from conftest import AuthActions
from pytodo.db import get_db


def test_index(client: FlaskClient, auth: AuthActions):
    # / redirects client to /tasks/
    response = client.get('/')
    assert response.headers['Location'] == '/tasks/'

    auth.login()

    # /tasks/ is successfull after loging in
    response = client.get('/tasks/')
    assert response.status_code == 200

    # The tasklist displays the correct information
    assert b'test' in response.data
    assert b'Log Out' in response.data
    assert b'Test description' in response.data
    assert b'todo-task-1' in response.data


@pytest.mark.parametrize('path', (
    '/tasks/',
    '/tasks/1/done',
    '/tasks/1/undone',
    '/tasks/1/delete'
))
def test_login_required(client: FlaskClient, path):
    # The routes redirect the client to /auth/login
    response = client.get(path)
    assert response.headers['Location'] == '/auth/login'


def test_create_task(client: FlaskClient, app: Flask, auth: AuthActions):
    auth.login()

    # Adding a task redirects to /tasks/
    response = client.post(
        '/tasks/create',
        data={'description': 'Added test task description.'}
    )
    assert response.headers['Location'] == '/tasks/'

    with app.app_context():

        # New task is added to the database
        new_task = get_db().execute(
            'SELECT * FROM task WHERE'
            ' description = "Added test task description." AND'
            ' user_id = 1',
        ).fetchone()
        assert new_task is not None

        # New task is displayed in the tasklist
        response = client.get('/tasks/')
        assert b'Added test task description.' in response.data


def test_complete_task(client: FlaskClient, app: Flask, auth: AuthActions):
    auth.login()

    # Client is redirected to /tasks/
    response = client.get('/tasks/1/done')
    assert response.headers['Location'] == '/tasks/'

    with app.app_context():

        # Completed task has an updated value of 1 for done (True)
        task = get_db().execute(
            'SELECT * FROM task WHERE id = 1'
        ).fetchone()
        assert task['done'] == True

    # Completed task is now in Completed tasks list
    response = client.get('/tasks/')
    assert b'completed-task-1' in response.data

    # Trying to complete a task that doesn't exist returns 404
    response = client.get('/tasks/10/done')
    assert response.status_code == 404

    # Trying to complete a task that the user doesn't own returns 403
    response = client.get('/tasks/2/done')


def test_uncomplete_task(client: FlaskClient, app: Flask, auth: AuthActions):
    auth.login()
    client.get('/tasks/1/done')

    # Client is redirected to /tasks/
    response = client.get('/tasks/1/undone')
    assert response.headers['Location'] == '/tasks/'

    with app.app_context():

        # Uncompleted task has an updated value of 1 for done (True)
        task = get_db().execute(
            'SELECT * FROM task WHERE id = 1'
        ).fetchone()
        assert task['done'] == False

    # Updated task is now in To Do tasks list
    response = client.get('/tasks/')
    assert b'todo-task-1' in response.data

    # Trying to complete a task that doesn't exist returns 404
    response = client.get('/tasks/10/undone')
    assert response.status_code == 404

    # Trying to complete a task that the user doesn't own returns 403
    response = client.get('/tasks/2/undone')


def test_delete_task(client: FlaskClient, app: Flask, auth: AuthActions):
    auth.login()

    # Client is redirected to /tasks/
    response = client.get('/tasks/1/delete')
    assert response.headers['Location'] == '/tasks/'

    with app.app_context():

        # Deleted Task is not in database anymore
        assert get_db().execute(
            'SELECT * FROM task WHERE description = "Test description"'
        ).fetchone() is None

    # Deleted task no longer displays in the task list
    response = client.get('/tasks/')
    assert b'Test description' not in response.data

    # Trying to delete a task that doesn't exist returns 404
    response = client.get('/tasks/10/delete')
    assert response.status_code == 404

    # Trying to delete a task that the user doesn't own returns 403
    response = client.get('/tasks/2/delete')
    assert response.status_code == 403
