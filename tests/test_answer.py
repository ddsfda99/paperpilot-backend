from unittest.mock import patch

def test_answer_success(client):
    """测试成功返回 AI 答案"""
    payload = {
        "file_id": "HEC.pdf",
        "question": "What is the main contribution of this paper?"
    }

    # mock get_context 和 requests.post
    with patch('routes.answer.get_context', return_value="This paper proposes a new method..."), \
         patch('routes.answer.requests.post') as mock_post:
        
        # 设置返回的内容结构
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {"message": {"content": "The main contribution is..."}}
            ]
        }

        res = client.post('/api/answer', json=payload)
        assert res.status_code == 200
        assert 'answer' in res.get_json()
        assert "main contribution" in res.get_json()['answer'].lower()

def test_answer_no_context(client):
    """测试上下文不存在"""
    payload = {
        "file_id": "nonexistent.pdf",
        "question": "Any insight?"
    }

    with patch('routes.answer.get_context', return_value=None):
        res = client.post('/api/answer', json=payload)
        assert res.status_code == 400
        assert 'error' in res.get_json()
        assert "上下文不存在" in res.get_json()['error']

def test_answer_llm_api_fail(client):
    """测试大模型 API 异常"""
    payload = {
        "file_id": "HEC.pdf",
        "question": "Explain the methodology."
    }

    with patch('routes.answer.get_context', return_value="Some context..."), \
         patch('routes.answer.requests.post', side_effect=Exception("LLM API failed")):

        res = client.post('/api/answer', json=payload)
        assert res.status_code == 500
        assert 'error' in res.get_json()
        assert "LLM API failed" in res.get_json()['error']
