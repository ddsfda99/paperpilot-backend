import os
import pytest
from flask import Flask
from routes.paper import paper_bp
from models import db, Paper

@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    app.register_blueprint(paper_bp)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def sample_paper(app):
    with app.app_context():
        paper = Paper(
            title="Test Paper",
            author="Tester",
            tags="AI",
            file_path="static/uploads/test_paper.pdf"
        )
        db.session.add(paper)
        db.session.commit()
        return paper  # 在 app_context 中创建并返回

def test_get_all_papers(client, sample_paper):
    res = client.get("/api/papers")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(p["title"] == "Test Paper" for p in data)

def test_delete_paper_success(client, app):
    with app.app_context():
        paper = Paper(
            title="To Be Deleted",
            author="Del",
            tags="AI",
            file_path="static/uploads/delete_me.pdf"
        )
        db.session.add(paper)
        db.session.commit()
        paper_id = paper.id
        abs_path = os.path.abspath(paper.file_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(b"dummy pdf content")

    res = client.delete(f"/api/papers/{paper_id}")
    assert res.status_code == 200
    assert "已删除文献" in res.get_json()["message"]
    assert not os.path.exists(abs_path)

def test_delete_paper_file_missing(client, app):
    with app.app_context():
        paper = Paper(
            title="Ghost Paper",
            author="Nobody",
            tags="None",
            file_path="static/uploads/nonexistent.pdf"
        )
        db.session.add(paper)
        db.session.commit()
        paper_id = paper.id

    res = client.delete(f"/api/papers/{paper_id}")
    assert res.status_code == 200
    assert "已删除文献" in res.get_json()["message"]

def test_download_paper_success(client, app):
    with app.app_context():
        paper = Paper(
            title="Downloadable",
            author="Author",
            tags="tag",
            file_path="static/uploads/download.pdf"
        )
        db.session.add(paper)
        db.session.commit()
        paper_id = paper.id
        abs_path = os.path.abspath(paper.file_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(b"%PDF-1.4 mock file")

    res = client.get(f"/api/papers/{paper_id}/download")
    assert res.status_code == 200
    assert res.headers["Content-Disposition"].startswith("attachment")
    assert res.data.startswith(b"%PDF")

def test_download_paper_not_found(client, app):
    with app.app_context():
        paper = Paper(
            title="Missing",
            author="Nobody",
            tags="None",
            file_path="static/uploads/missing.pdf"
        )
        db.session.add(paper)
        db.session.commit()
        paper_id = paper.id

    res = client.get(f"/api/papers/{paper_id}/download")
    assert res.status_code == 404
    assert res.get_json()["error"] == "文件不存在"
