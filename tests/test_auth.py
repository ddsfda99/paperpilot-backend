def test_register_success(client, db):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': '123456'
    })
    assert response.status_code == 200
    assert response.json['msg'] == '注册成功'

def test_register_duplicate(client, db):
    # 再次注册相同用户名，应该失败
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'newpass'
    })
    assert response.status_code == 400
    assert '用户名已存在' in response.json['msg']

def test_login_success(client, db):
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': '123456'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['username'] == 'testuser'

def test_login_fail(client, db):
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['msg'] == '用户名或密码错误'
