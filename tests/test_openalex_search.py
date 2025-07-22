import pytest
from unittest.mock import patch
from flask import Flask
from routes.openalex_search import openalex_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(openalex_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def mock_openalex_response(*args, **kwargs):
    return {
        "results": [
            {
                "title": "Test Paper",
                "authorships": [
                    {"author": {"display_name": "Alice"}},
                    {"author": {"display_name": "Bob"}}
                ],
                "abstract_inverted_index": {
                    "This": [0],
                    "is": [1],
                    "a": [2],
                    "test": [3]
                },
                "id": "https://openalex.org/test-id"
            }
        ]
    }

@patch("routes.openalex_search.requests.get")
def test_openalex_search_success(mock_get, client):
    # 模拟 OpenAlex 的响应
    mock_get.return_value.status_code = 200
    mock_get.return_value.json = mock_openalex_response

    response = client.get("/api/openalex/search?q=test")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test Paper"
    assert data[0]["authors"] == ["Alice", "Bob"]
    assert data[0]["abstract"] == "This is a test"
    assert data[0]["link"] == "https://openalex.org/test-id"

def test_openalex_search_missing_query(client):
    response = client.get("/api/openalex/search")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing query parameter"

@patch("routes.openalex_search.requests.get")
def test_openalex_search_openalex_error(mock_get, client):
    mock_get.side_effect = Exception("OpenAlex timeout")

    response = client.get("/api/openalex/search?q=timeout")
    assert response.status_code == 500
    assert "OpenAlex timeout" in response.get_json()["error"]
