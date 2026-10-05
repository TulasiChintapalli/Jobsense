import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from .extensions import db, jwt
load_dotenv()

def fail(msg, code=400):
    return jsonify(success=False, message=msg), code

def ok(data=None, msg="OK", code=200):
    return jsonify(success=True, message=msg, data=data or {}), code

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    secret = os.getenv("SECRET_KEY", "dev-only-change-me")
    app.config.update(
        SECRET_KEY=secret, JWT_SECRET_KEY=secret,
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///app.db"),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024,
    )
    CORS(app, origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")])
    db.init_app(app); jwt.init_app(app)

    @jwt.unauthorized_loader
    def _u(m): return fail("Please log in to continue.", 401)
    @jwt.expired_token_loader
    def _e(h, p): return fail("Session expired. Please log in again.", 401)
    @jwt.invalid_token_loader
    def _i(m): return fail("Invalid session. Please log in again.", 401)
    @app.errorhandler(413)
    def _big(e): return fail("File is too large.", 413)
    @app.errorhandler(Exception)
    def _any(e):
        app.logger.exception(e)
        code = getattr(e, "code", 500)
        return fail("Something went wrong." if code == 500 else str(e), code if isinstance(code, int) else 500)

    from .routes import auth, analysis, dashboard, profile, ml
    for m in (auth, analysis, dashboard, profile, ml):
        app.register_blueprint(m.bp)
    with app.app_context():
        from .models import user, analysis as _a  # noqa
        db.create_all()
    return app
