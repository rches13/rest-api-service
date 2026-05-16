import pytest


@pytest.fixture
def auth_headers(client):
    client.post('/api/auth/register', json={
        'username': 'taskuser', 'email': 'tasks@example.com', 'password': 'pass123'
    })
    res = client.post('/api/auth/login', json={'email': 'tasks@example.com', 'password': 'pass123'})
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


def test_create_task(client, auth_headers):
    res = client.post('/api/tasks', json={'title': 'Buy groceries', 'priority': 'high'}, headers=auth_headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data['title'] == 'Buy groceries'
    assert data['status'] == 'todo'
    assert data['priority'] == 'high'


def test_create_task_missing_title(client, auth_headers):
    res = client.post('/api/tasks', json={'priority': 'low'}, headers=auth_headers)
    assert res.status_code == 400


def test_get_tasks(client, auth_headers):
    client.post('/api/tasks', json={'title': 'Task 1'}, headers=auth_headers)
    client.post('/api/tasks', json={'title': 'Task 2'}, headers=auth_headers)
    res = client.get('/api/tasks', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()['total'] == 2


def test_get_tasks_filter_by_status(client, auth_headers):
    client.post('/api/tasks', json={'title': 'Todo task', 'status': 'todo'}, headers=auth_headers)
    client.post('/api/tasks', json={'title': 'Done task', 'status': 'done'}, headers=auth_headers)
    res = client.get('/api/tasks?status=done', headers=auth_headers)
    data = res.get_json()
    assert data['total'] == 1
    assert data['tasks'][0]['status'] == 'done'


def test_get_single_task(client, auth_headers):
    res = client.post('/api/tasks', json={'title': 'Single'}, headers=auth_headers)
    task_id = res.get_json()['id']
    res = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()['title'] == 'Single'


def test_update_task(client, auth_headers):
    res = client.post('/api/tasks', json={'title': 'Update me'}, headers=auth_headers)
    task_id = res.get_json()['id']
    res = client.put(f'/api/tasks/{task_id}', json={'status': 'done', 'title': 'Updated'}, headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'done'
    assert data['title'] == 'Updated'


def test_delete_task(client, auth_headers):
    res = client.post('/api/tasks', json={'title': 'Delete me'}, headers=auth_headers)
    task_id = res.get_json()['id']
    res = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
    assert res.status_code == 204
    res = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    assert res.status_code == 404


def test_unauthorized_access(client):
    res = client.get('/api/tasks')
    assert res.status_code == 401


def test_cannot_access_other_users_task(client, auth_headers):
    res = client.post('/api/tasks', json={'title': 'Private task'}, headers=auth_headers)
    task_id = res.get_json()['id']

    client.post('/api/auth/register', json={
        'username': 'other', 'email': 'other@example.com', 'password': 'pass'
    })
    res2 = client.post('/api/auth/login', json={'email': 'other@example.com', 'password': 'pass'})
    other_headers = {'Authorization': f"Bearer {res2.get_json()['token']}"}

    res = client.get(f'/api/tasks/{task_id}', headers=other_headers)
    assert res.status_code == 404
