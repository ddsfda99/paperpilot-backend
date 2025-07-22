import pytest
from flask import Flask
import json

from routes.explain import explain_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(explain_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_explain_success(client, monkeypatch):
    # 模拟 AI 接口响应
    def mock_post(url, headers=None, json=None):
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                return {
                    "choices": [{
                        "message": {
                            "content": "这是模拟解释结果。"
                        }
                    }]
                }
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)

    res = client.post('/api/explain', json={"text": "What is transformer architecture?"})
    assert res.status_code == 200
    data = res.get_json()
    assert "explanation" in data
    assert data["explanation"] == "这是模拟解释结果。"

def test_explain_empty_text(client):
    res = client.post('/api/explain', json={"text": ""})
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
