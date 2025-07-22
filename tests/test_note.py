def test_create_note(client, db):
    """测试创建笔记"""
    payload = {'title': 'Test Title', 'content': 'Test Content'}
    res = client.post('/api/notes', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['title'] == 'Test Title'
    assert data['content'] == 'Test Content'
    assert 'id' in data

def test_get_notes(client, db):
    """测试获取所有笔记"""
    # 创建 2 条笔记
    client.post('/api/notes', json={'title': 'First', 'content': 'A'})
    client.post('/api/notes', json={'title': 'Second', 'content': 'B'})

    res = client.get('/api/notes')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert all('title' in note and 'content' in note for note in data)

def test_update_note(client, db):
    """测试更新笔记"""
    # 创建一条
    res = client.post('/api/notes', json={'title': 'Old Title', 'content': 'Old Content'})
    note_id = res.get_json()['id']

    # 更新该条
    updated = {'title': 'New Title', 'content': 'New Content'}
    res2 = client.put(f'/api/notes/{note_id}', json=updated)
    assert res2.status_code == 200
    data = res2.get_json()
    assert data['title'] == 'New Title'
    assert data['content'] == 'New Content'

def test_delete_note(client, db):
    """测试删除笔记"""
    res = client.post('/api/notes', json={'title': 'To Delete', 'content': 'Delete this'})
    note_id = res.get_json()['id']

    res2 = client.delete(f'/api/notes/{note_id}')
    assert res2.status_code == 200
    assert res2.get_json() == {'success': True}

    # 确认删除后无法更新
    res3 = client.put(f'/api/notes/{note_id}', json={'title': 'Oops'})
    assert res3.status_code == 404
