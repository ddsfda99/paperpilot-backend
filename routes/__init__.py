from .upload import upload_bp
from .ask import ask_bp
from .explain import explain_bp
from .paper import paper_bp
from .auth import auth_bp
from .answer import answer_bp
from .openalex_search import openalex_bp
from .extract_references import extract_bp
from .openalex_recommend import recommend_bp

def register_routes(app):
    app.register_blueprint(upload_bp)
    app.register_blueprint(ask_bp)
    app.register_blueprint(explain_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(answer_bp)
    app.register_blueprint(openalex_bp)
    app.register_blueprint(extract_bp)
    app.register_blueprint(recommend_bp)