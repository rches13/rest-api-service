def test_register(client):
    res = client.post('/api/auth/register', json={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'token' in data
    assert data['user']['email'] == 'test@example.com'


def test_register_missing_fields(client):
    res = client.post('/api/auth/register', json={'username': 'only'})
    assert res.status_code == 400


def test_register_duplicate_email(client):
    payload = {'username': 'user1', 'email': 'dupe@example.com', 'password': 'pass123'}
    client.post('/api/auth/register', json=payload)
    payload['username'] = 'user2'
    res = client.post('/api/auth/register', json=payload)
    assert res.status_code == 409


def test_login(client):
    client.post('/api/auth/register', json={
        'username': 'loginuser', 'email': 'login@example.com', 'password': 'secret'
    })
    res = client.post('/api/auth/login', json={'email': 'login@example.com', 'password': 'secret'})
    assert res.status_code == 200
    assert 'token' in res.get_json()


def test_login_wrong_password(client):
    client.post('/api/auth/register', json={
        'username': 'badpass', 'email': 'bad@example.com', 'password': 'correct'
    })
    res = client.post('/api/auth/login', json={'email': 'bad@example.com', 'password': 'wrong'})
    assert res.status_code == 401
