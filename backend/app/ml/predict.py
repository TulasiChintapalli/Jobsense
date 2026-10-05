import json
import os

import joblib

from .preprocess import clean_text


# --------------------------------------------------
# MODEL ARTIFACTS
# --------------------------------------------------

ART = os.path.join(
    os.path.dirname(__file__),
    "artifacts"
)

_cache = {}


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

def _load():
    if "m" not in _cache:

        vectorizer_path = os.path.join(
            ART,
            "tfidf_vectorizer.pkl"
        )

        model_path = os.path.join(
            ART,
            "job_role_model.pkl"
        )

        # Check whether trained model exists
        if not (
            os.path.exists(vectorizer_path)
            and os.path.exists(model_path)
        ):
            return None

        _cache["v"] = joblib.load(
            vectorizer_path
        )

        _cache["m"] = joblib.load(
            model_path
        )

    return _cache


# --------------------------------------------------
# PREDICT JOB FUNCTION
# --------------------------------------------------

def predict_role(text):

    model_data = _load()

    if not model_data:
        return None

    vectorizer = model_data["v"]
    model = model_data["m"]

    # Clean job description
    cleaned_text = clean_text(text)

    # Convert text into TF-IDF features
    features = vectorizer.transform(
        [cleaned_text]
    )

    # Get probabilities for all 37 job functions
    probabilities = model.predict_proba(
        features
    )[0]

    # Find highest probability
    best_index = probabilities.argmax()

    prediction = model.classes_[best_index]

    confidence = probabilities[best_index]

    return {
        "prediction": str(prediction),
        "confidence": round(
            float(confidence),
            4
        )
    }


# --------------------------------------------------
# LOAD MODEL METRICS
# --------------------------------------------------

def load_metrics():

    metrics_file = os.path.join(
        ART,
        "metrics.json"
    )

    if not os.path.exists(
        metrics_file
    ):
        return None

    with open(
        metrics_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)