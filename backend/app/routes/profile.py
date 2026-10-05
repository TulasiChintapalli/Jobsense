from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import ok, fail
from ..extensions import db
from ..models.user import User
bp = Blueprint("profile", __name__, url_prefix="/api/profile")

@bp.get("")
@jwt_required()
def get_profile(): return ok(dict(user=db.session.get(User, int(get_jwt_identity())).to_dict()))

@bp.put("")
@jwt_required()
def update():
    name = ((request.get_json(silent=True) or {}).get("full_name") or "").strip()
    if not name: return fail("Name cannot be empty.")
    u = db.session.get(User, int(get_jwt_identity())); u.full_name = name[:120]; db.session.commit()
    return ok(dict(user=u.to_dict()), "Profile updated")
