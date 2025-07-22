import pytest
import json
from flask import Flask
from routes.openalex_recommend import recommend_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(recommend_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_recommend_success(client, requests_mock):
    # 模拟 OpenAlex 返回数据
    mock_data = {
        "results": [
            {
                "title": "Test Paper",
                "authorships": [
                    {"author": {"display_name": "Alice"}},
                    {"author": {"display_name": "Bob"}}
                ],
                "abstract_inverted_index": {
                    "deep": [0],
                    "learning": [1]
                },
                "primary_location": {
                    "landing_page_url": "http://example.com/paper"
                }
            }
        ]
    }
    requests_mock.get(
        "https://api.openalex.org/works",
        json=mock_data,
        status_code=200
    )

    payload = {
        "selected_keywords": ["deep learning"]
    }

    response = client.post("/api/openalex/recommend", json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Test Paper"
    assert "deep learning" in data[0]["abstract"]

def test_recommend_no_keywords(client):
    payload = {
        "selected_keywords": [],
        "keyword": "",
        "text": ""
    }
    res = client.post("/api/openalex/recommend", json=payload)
    assert res.status_code == 400
    assert res.get_json()["error"] == "缺少关键词"

def test_recommend_api_failure(client, requests_mock):
    requests_mock.get(
        "https://api.openalex.org/works",
        status_code=500
    )

    payload = {
        "keyword": "AI"
    }

    res = client.post("/api/openalex/recommend", json=payload)
    assert res.status_code == 500
    assert res.get_json() == []
