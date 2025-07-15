from flask import Flask
from models import db
from flask_cors import CORS
from routes import register_routes
import sys
import os

sys.path.append(os.path.dirname(__file__))

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    app.config.from_pyfile('config.py')

    db.init_app(app)

    # ✅ 正确配置跨域支持
    CORS(app, resources={r"/*": {"origins": "*"}})

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)
