import re
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .. import ok, fail
from ..extensions import db
from ..models.user import User
bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@bp.post("/register")
def register():
    d = request.get_json(silent=True) or {}
    name, email, pw = (d.get("full_name") or "").strip(), (d.get("email") or "").strip().lower(), d.get("password") or ""
    if not name or not EMAIL.match(email): return fail("Enter your name and a valid email.")
    if len(pw) < 8: return fail("Password must be at least 8 characters.")
    if User.query.filter_by(email=email).first(): return fail("That email is already registered.", 409)
    u = User(full_name=name, email=email); u.set_password(pw)
    db.session.add(u); db.session.commit()
    return ok(dict(token=create_access_token(identity=str(u.id)), user=u.to_dict()), "Account created", 201)

@bp.post("/login")
def login():
    d = request.get_json(silent=True) or {}
    u = User.query.filter_by(email=(d.get("email") or "").strip().lower()).first()
    if not u or not u.check_password(d.get("password") or ""): return fail("Incorrect email or password.", 401)
    return ok(dict(token=create_access_token(identity=str(u.id)), user=u.to_dict()), "Logged in")

@bp.get("/me")
@jwt_required()
def me():
    u = db.session.get(User, int(get_jwt_identity()))
    return ok(dict(user=u.to_dict())) if u else fail("User not found.", 404)
