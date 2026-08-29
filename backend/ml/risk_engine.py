"""Risk orchestration for predictive camera failures and escalation triggers."""

from datetime import datetime

from database import connect, row_to_dict
from ml.feature_extractor import extract_features
from ml.trainer import load_models, save_models, train_models


def get_recommended_action(risk_level, features=None):
    """Return operational guidance for the predicted risk level."""
    return {
        "LOW": "No action required. Monitor normally.",
        "MEDIUM": "Schedule a physical inspection within 72 hours.",
        "HIGH": "Inspect physical connection and switch port immediately.",
        "CRITICAL": "Dispatch maintenance team now. Camera failure imminent.",
        "UNKNOWN": "Insufficient monitoring history. Continue collecting health samples.",
        "PENDING": "Prediction model is being prepared. Run analysis again after training completes.",
    }.get(risk_level, "Review camera health history and validate the network path.")


def train_from_database():
    """Train and persist models from the current SQLite monitoring history."""
    with connect() as db:
        cameras = db.execute("SELECT id FROM cameras ORDER BY id").fetchall()
        feature_matrix = []
        for camera in cameras:
            features = extract_features(camera["id"], db)
            if features:
                feature_matrix.append(features)
    models = train_models(feature_matrix)
    if models:
        save_models(models)
    return bool(models)


def ensure_models():
    """Auto-train models on startup when no persisted model files exist."""
    if load_models() is not None:
        return True
    return train_from_database()


def run_all_predictions():
    """Generate a fresh prediction for every registered camera."""
    from ml.predictor import predict_risk
    results = []
    with connect() as db:
        cameras = [row_to_dict(row) for row in db.execute("SELECT id FROM cameras ORDER BY id").fetchall()]
    for camera in cameras:
        results.append(predict_risk(camera["id"]))
    return results


def latest_predictions():
    """Return the latest prediction row for each camera."""
    with connect() as db:
        rows = db.execute(
            """
            SELECT p.camera_id, c.name AS camera_name, p.risk_score, p.risk_level,
                   p.predicted_failure_window, p.recommended_action, p.created_at
            FROM predictions p
            JOIN cameras c ON c.id = p.camera_id
            JOIN (
                SELECT camera_id, MAX(created_at) AS latest_at
                FROM predictions
                GROUP BY camera_id
            ) latest ON latest.camera_id = p.camera_id AND latest.latest_at = p.created_at
            ORDER BY c.id
            """
        ).fetchall()
        existing = [row_to_dict(row) for row in rows]
        if existing:
            return existing
        cameras = db.execute("SELECT id AS camera_id, name AS camera_name FROM cameras ORDER BY id").fetchall()
        now = datetime.now().isoformat(timespec="seconds")
        return [
            {
                "camera_id": row["camera_id"],
                "camera_name": row["camera_name"],
                "risk_score": 0,
                "risk_level": "PENDING" if load_models() is None else "UNKNOWN",
                "predicted_failure_window": "Pending analysis",
                "recommended_action": get_recommended_action("PENDING" if load_models() is None else "UNKNOWN"),
                "created_at": now,
            }
            for row in cameras
        ]
