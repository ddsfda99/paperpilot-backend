import pytest
from unittest.mock import patch
from flask import Flask
from routes.semantic_answer import semantic_answer_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(semantic_answer_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@patch("routes.semantic_answer.retrieve_context")
@patch("routes.semantic_answer.requests.post")
def test_semantic_answer_success(mock_post, mock_retrieve, client):
    mock_retrieve.return_value = [
        "This is paragraph 1.",
        "This is paragraph 2.",
        "This is paragraph 3.",
        "This is paragraph 4.",
        "This is paragraph 5."
    ]

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {
                "content": "This is the model's answer."
            }
        }]
    }

    payload = {
        "file_id": "HEC.pdf",
        "question": "What is the main contribution of this paper?"
    }

    res = client.post("/api/semantic_answer", json=payload)
    assert res.status_code == 200
    assert res.get_json()["answer"] == "This is the model's answer."

@patch("routes.semantic_answer.retrieve_context")
def test_semantic_answer_no_chunks(mock_retrieve, client):
    mock_retrieve.return_value = []

    payload = {
        "file_id": "HEC.pdf",
        "question": "No context?"
    }

    res = client.post("/api/semantic_answer", json=payload)
    assert res.status_code == 400
    assert "未找到相关段落" in res.get_json()["error"]

@patch("routes.semantic_answer.retrieve_context", return_value=["dummy context"])
@patch("routes.semantic_answer.requests.post")
def test_semantic_answer_model_failure(mock_post, mock_retrieve, client):
    mock_post.side_effect = Exception("API timeout")

    payload = {
        "file_id": "HEC.pdf",
        "question": "Trigger failure"
    }

    res = client.post("/api/semantic_answer", json=payload)
    assert res.status_code == 500
    assert "大模型调用失败" in res.get_json()["error"]
