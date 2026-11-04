"""Model training and persistence for predictive camera failure analysis.

The preferred backend is scikit-learn RandomForestClassifier and IsolationForest. If the local
Windows policy blocks SciPy native DLL loading, this module falls back to small pickleable models
that preserve the same predict_proba and decision_function contract so the application remains live.
"""

import hashlib
import hmac
import logging
import math
import pickle
from pathlib import Path

from config import JWT_SECRET

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    SKLEARN_AVAILABLE = True
except Exception:
    IsolationForest = None
    RandomForestClassifier = None
    SKLEARN_AVAILABLE = False

from ml.feature_extractor import feature_names

MODEL_DIR = Path(__file__).resolve().parent / "models"
RF_PATH = MODEL_DIR / "risk_random_forest.pkl"
IF_PATH = MODEL_DIR / "risk_isolation_forest.pkl"
META_PATH = MODEL_DIR / "metadata.pkl"


class FallbackRiskClassifier:
    """Small deterministic classifier used when scikit-learn cannot load."""

    classes_ = ["HIGH", "LOW"]

    def fit(self, rows, labels):
        return self

    def predict_proba(self, rows):
        output = []
        names = feature_names()
        avg_idx = names.index("avg_latency")
        off_idx = names.index("offline_frequency")
        anom_idx = names.index("anomaly_rate")
        recent_idx = names.index("recent_instability")
        loss_idx = names.index("packet_loss_avg")
        for row in rows:
            score = 0.0
            score += min(row[avg_idx] / 200, 1) * 0.25
            score += min(row[off_idx], 1) * 0.35
            score += min(row[anom_idx], 1) * 0.15
            score += min(row[recent_idx], 1) * 0.15
            score += min(row[loss_idx] / 100, 1) * 0.10
            high = max(0.0, min(1.0, score))
            output.append([high, 1.0 - high])
        return output


class FallbackIsolationModel:
    """Approximate anomaly scoring model with an IsolationForest-like API."""

    def fit(self, rows):
        if not rows:
            self.center = []
            self.scale = []
            return self
        columns = list(zip(*rows))
        self.center = [sum(col) / len(col) for col in columns]
        self.scale = []
        for index, col in enumerate(columns):
            avg = self.center[index]
            variance = sum((value - avg) ** 2 for value in col) / len(col)
            self.scale.append(math.sqrt(variance) or 1.0)
        return self

    def decision_function(self, rows):
        values = []
        for row in rows:
            if not getattr(self, "center", None):
                values.append(0.1)
                continue
            distance = sum(abs(value - self.center[index]) / self.scale[index] for index, value in enumerate(row)) / len(row)
            values.append(0.2 - min(distance / 10, 0.4))
        return values


def _label(features):
    if features.get("offline_frequency", 0) > 0.3 or features.get("avg_latency", 0) > 100:
        return "HIGH"
    return "LOW"


def train_models(feature_matrix):
    """Train RandomForest and IsolationForest models from extracted camera features."""
    if not feature_matrix:
        return None
    names = feature_names()
    x_rows = [[float(features.get(name, 0.0) or 0.0) for name in names] for features in feature_matrix]
    y_rows = [_label(features) for features in feature_matrix]
    if len(set(y_rows)) == 1:
        synthetic = dict(feature_matrix[0])
        synthetic["avg_latency"] = 180 if y_rows[0] == "LOW" else 20
        synthetic["offline_frequency"] = 0.4 if y_rows[0] == "LOW" else 0.0
        feature_matrix = list(feature_matrix) + [synthetic]
        x_rows = [[float(features.get(name, 0.0) or 0.0) for name in names] for features in feature_matrix]
        y_rows = [_label(features) for features in feature_matrix]
    if SKLEARN_AVAILABLE:
        rf = RandomForestClassifier(n_estimators=80, random_state=42, class_weight="balanced")
        iso = IsolationForest(contamination=0.1, random_state=42)
    else:
        rf = FallbackRiskClassifier()
        iso = FallbackIsolationModel()
    rf.fit(x_rows, y_rows)
    iso.fit(x_rows)
    return {"random_forest": rf, "isolation_forest": iso, "feature_names": names, "backend": "sklearn" if SKLEARN_AVAILABLE else "fallback"}


def _compute_model_sig(rf_bytes, iso_bytes, meta_bytes):
    key = (JWT_SECRET or "cctv-ml-signing-key").encode("utf-8")
    h = hmac.new(key, digestmod=hashlib.sha256)
    h.update(rf_bytes)
    h.update(iso_bytes)
    h.update(meta_bytes)
    return h.hexdigest()


def save_models(models, path=None):
    """Persist trained models with HMAC signature verification."""
    if not models:
        return False
    directory = Path(path) if path else MODEL_DIR
    directory.mkdir(parents=True, exist_ok=True)
    rf_bytes = pickle.dumps(models["random_forest"])
    iso_bytes = pickle.dumps(models["isolation_forest"])
    meta_bytes = pickle.dumps({"feature_names": models["feature_names"], "backend": models.get("backend", "unknown")})
    sig = _compute_model_sig(rf_bytes, iso_bytes, meta_bytes)
    with open(directory / RF_PATH.name, "wb") as handle:
        handle.write(rf_bytes)
    with open(directory / IF_PATH.name, "wb") as handle:
        handle.write(iso_bytes)
    with open(directory / META_PATH.name, "wb") as handle:
        handle.write(meta_bytes)
    with open(directory / "models.sig", "w", encoding="utf-8") as handle:
        handle.write(sig)
    return True


def load_models(path=None):
    """Load persisted models after verifying HMAC signature integrity."""
    directory = Path(path) if path else MODEL_DIR
    rf_path = directory / RF_PATH.name
    if_path = directory / IF_PATH.name
    meta_path = directory / META_PATH.name
    sig_path = directory / "models.sig"
    if not rf_path.exists() or not if_path.exists() or not meta_path.exists() or not sig_path.exists():
        return None
    rf_bytes = rf_path.read_bytes()
    iso_bytes = if_path.read_bytes()
    meta_bytes = meta_path.read_bytes()
    expected_sig = _compute_model_sig(rf_bytes, iso_bytes, meta_bytes)
    actual_sig = sig_path.read_text(encoding="utf-8").strip()
    if not hmac.compare_digest(actual_sig, expected_sig):
        logging.error("ML model HMAC signature mismatch! Rejecting untrusted model pickle.")
        return None
    rf = pickle.loads(rf_bytes)
    iso = pickle.loads(iso_bytes)
    meta = pickle.loads(meta_bytes)
    return {"random_forest": rf, "isolation_forest": iso, "feature_names": meta.get("feature_names", feature_names()), "backend": meta.get("backend", "unknown")}
