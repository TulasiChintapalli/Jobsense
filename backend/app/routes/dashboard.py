import json
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from .. import ok
from ..extensions import db
from ..models.analysis import Analysis
bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@bp.get("/stats")
@jwt_required()
def stats():
    uid = int(get_jwt_identity())
    q = Analysis.query.filter_by(user_id=uid)
    avg = db.session.query(func.avg(Analysis.overall_score)).filter(Analysis.user_id == uid).scalar()
    skills = set()
    for a in q.all():
        if a.result: skills.update(s.lower() for s in json.loads(a.result.technical_skills or "[]"))
    series = [dict(date=a.created_at.date().isoformat(), score=a.overall_score)
              for a in q.filter(Analysis.overall_score.isnot(None)).order_by(Analysis.created_at).limit(20)]
    recent = q.order_by(Analysis.created_at.desc()).limit(5).all()
    return ok(dict(total=q.count(), average_score=round(avg) if avg is not None else None,
                   skills_identified=len(skills), recent=[a.to_dict() for a in recent], score_series=series))
