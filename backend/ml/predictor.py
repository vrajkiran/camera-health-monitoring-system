"""Prediction API for per-camera failure risk assessment."""

import json
from datetime import datetime

from database import connect
from ml.feature_extractor import extract_features, to_vector
from ml.risk_engine import get_recommended_action
from ml.trainer import load_models


def _score_to_level(score):
    if score <= 30:
        return "LOW", "No failure expected"
    if score <= 60:
        return "MEDIUM", "72 HOURS"
    if score <= 85:
        return "HIGH", "24 HOURS"
    return "CRITICAL", "6 HOURS"


def _rf_score(model, vector):
    probabilities = model.predict_proba([vector])[0]
    classes = list(model.classes_)
    weighted = 0.0
    weights = {"LOW": 15, "MEDIUM": 45, "HIGH": 75, "CRITICAL": 95}
    for index, label in enumerate(classes):
        weighted += probabilities[index] * weights.get(label, 50)
    return weighted


def _if_score(model, vector):
    raw = model.decision_function([vector])[0]
    anomaly = max(0.0, min(1.0, (0.2 - raw) / 0.4))
    return anomaly * 100


def _insert_prediction(camera_id, risk_score, risk_level, window, action, features):
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as db:
        db.execute(
            """
            INSERT INTO predictions
            (camera_id, risk_score, risk_level, predicted_failure_window, recommended_action, features_snapshot, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (camera_id, risk_score, risk_level, window, action, json.dumps(features or {}, ensure_ascii=False), now),
        )
        camera = db.execute("SELECT name FROM cameras WHERE id = ?", (camera_id,)).fetchone()
    return {
        "camera_id": camera_id,
        "camera_name": camera["name"] if camera else "Unknown camera",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "predicted_failure_window": window,
        "recommended_action": action,
        "created_at": now,
    }


def predict_risk(camera_id):
    """Predict one camera's failure risk and store the result in SQLite."""
    models = load_models()
    if models is None:
        return _insert_prediction(camera_id, 0, "PENDING", "Pending analysis", get_recommended_action("PENDING"), {})
    with connect() as db:
        features = extract_features(camera_id, db)
    if features is None:
        return _insert_prediction(camera_id, 0, "UNKNOWN", "Insufficient data", get_recommended_action("UNKNOWN"), {})
    vector = to_vector(features)
    rf_component = _rf_score(models["random_forest"], vector)
    if_component = _if_score(models["isolation_forest"], vector)
    score = int(round(max(0, min(100, rf_component * 0.65 + if_component * 0.35))))
    level, window = _score_to_level(score)
    action = get_recommended_action(level, features)
    result = _insert_prediction(camera_id, score, level, window, action, features)
    if level in ("HIGH", "CRITICAL"):
        try:
            from escalation_engine import EscalationEngine
            EscalationEngine().trigger(camera_id, "PREDICTED_FAILURE")
        except Exception:
            pass
    return result
