from .upload import upload_bp
from .ask import ask_bp
from .explain import explain_bp
from .paper import paper_bp
from .auth import auth_bp
from .answer import answer_bp
from .search import search_bp

def register_routes(app):
    app.register_blueprint(upload_bp)
    app.register_blueprint(ask_bp)
    app.register_blueprint(explain_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(answer_bp)
    app.register_blueprint(search_bp)