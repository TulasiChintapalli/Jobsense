from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from .. import ok, fail
from ..ml import predict as P


bp = Blueprint("ml", __name__, url_prefix="/api/ml")


@bp.post("/predict")
@jwt_required()
def predict():
    text = (
        (request.get_json(silent=True) or {})
        .get("job_description") or ""
    ).strip()

    if not text:
        return fail("Job description is required.")

    r = P.predict_role(text)

    if r is None:
        return fail(
            "ML prediction is unavailable because the model has not been trained yet.",
            503
        )

    return jsonify(
        success=True,
        prediction=r["prediction"],
        confidence=r["confidence"],
        note="Model confidence, not certainty."
    )


@bp.get("/info")
@jwt_required()
def info():
    return ok(
        dict(
            model="TF-IDF + Logistic Regression",
            purpose="Job function classification",
            metrics=P.load_metrics()
        )
    )