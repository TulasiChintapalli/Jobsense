import json
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import ok, fail
from ..extensions import db
from ..models.analysis import Analysis, AnalysisResult, LISTS
from ..services import ai_service, file_service
from ..ml import predict as P

bp = Blueprint("analysis", __name__, url_prefix="/api")


def _run(text, file_name=None):
    text = (text or "").strip()

    if len(text) < 50:
        return fail("Job description is too short to analyze.")

    # -----------------------------
    # ML prediction
    # -----------------------------
    ml = None
    ml_error = None

    try:
        ml = P.predict_role(text)
    except Exception as e:
        print("ML prediction unavailable:", e)
        ml_error = "ML prediction is currently unavailable."

    # -----------------------------
    # AI analysis
    # -----------------------------
    ai, ai_err = ai_service.analyze(text)

    # -----------------------------
    # Create analysis record
    # -----------------------------
    a = Analysis(
        user_id=int(get_jwt_identity()),
        original_text=text,
        file_name=file_name,
        ml_prediction=ml["prediction"] if ml else None,
        ml_confidence=ml["confidence"] if ml else None
    )

    # -----------------------------
    # Store AI result
    # -----------------------------
    if ai:
        a.job_title = ai["job_title"]
        a.company_name = ai["company_name"]
        a.overall_score = ai["overall_score"]

        a.result = AnalysisResult(
            summary=ai["summary"],
            **{k: json.dumps(ai[k]) for k in LISTS}
        )

    # -----------------------------
    # Analysis title
    # -----------------------------
    a.title = (
        a.job_title
        if ai and a.job_title != "Not specified"
        else (a.ml_prediction or "Untitled analysis")
    )

    # -----------------------------
    # Save to database
    # -----------------------------
    db.session.add(a)
    db.session.commit()

    # -----------------------------
    # Response
    # -----------------------------
    d = a.to_dict(True)

    warnings = []

    if ml_error:
        warnings.append(ml_error)

    if ai_err:
        warnings.append(ai_err)

    d["warnings"] = warnings

    return ok(d, "Analysis complete", 201)


@bp.post("/analyze")
@jwt_required()
def analyze():
    data = request.get_json(silent=True) or {}
    return _run(data.get("job_description"))


@bp.post("/analyze/upload")
@jwt_required()
def upload():
    f = request.files.get("file")

    if not f or not f.filename:
        return fail("Choose a file to upload.")

    try:
        text = file_service.extract_text(f)
    except ValueError as e:
        return fail(str(e))

    return _run(text, f.filename)


@bp.get("/analyses")
@jwt_required()
def list_all():
    q = Analysis.query.filter_by(
        user_id=int(get_jwt_identity())
    )

    s = (request.args.get("search") or "").strip()

    if s:
        like = f"%{s}%"

        q = q.filter(
            db.or_(
                Analysis.title.ilike(like),
                Analysis.company_name.ilike(like),
                Analysis.ml_prediction.ilike(like)
            )
        )

    col = {
        "score": Analysis.overall_score,
        "title": Analysis.title
    }.get(
        request.args.get("sort"),
        Analysis.created_at
    )

    q = q.order_by(
        col.asc()
        if request.args.get("order") == "asc"
        else col.desc()
    )

    return ok(
        dict(
            analyses=[
                a.to_dict()
                for a in q.all()
            ]
        )
    )


def _owned(id):
    return Analysis.query.filter_by(
        id=id,
        user_id=int(get_jwt_identity())
    ).first()


@bp.get("/analyses/<int:id>")
@jwt_required()
def get_one(id):
    a = _owned(id)

    return (
        ok(a.to_dict(True))
        if a
        else fail("Analysis not found.", 404)
    )


@bp.delete("/analyses/<int:id>")
@jwt_required()
def delete(id):
    a = _owned(id)

    if not a:
        return fail("Analysis not found.", 404)

    db.session.delete(a)
    db.session.commit()

    return ok(msg="Analysis deleted")