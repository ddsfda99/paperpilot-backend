import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app 
from models import db as _db
import tempfile

@pytest.fixture(scope='module')
def app():
    app = create_app(testing=True)  
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def db(app):
    _db.create_all()
    yield _db
    _db.drop_all()
