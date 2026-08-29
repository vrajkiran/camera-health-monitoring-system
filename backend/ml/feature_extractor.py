"""Feature extraction utilities for predictive CCTV failure analysis."""

import math


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def _stddev(values):
    if len(values) < 2:
        return 0.0
    avg = _mean(values)
    variance = sum((value - avg) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def _window_metrics(rows, prefix=""):
    total = len(rows)
    latencies = [row["response_time_ms"] for row in rows if row["response_time_ms"] is not None]
    null_count = sum(1 for row in rows if row["response_time_ms"] is None)
    anomaly_count = sum(1 for row in rows if row["is_anomaly"])
    packet_losses = [row["packet_loss_pct"] or 0 for row in rows]
    return {
        f"{prefix}avg_latency": _mean(latencies),
        f"{prefix}max_latency": max(latencies) if latencies else 0.0,
        f"{prefix}latency_stddev": _stddev(latencies),
        f"{prefix}null_count": null_count,
        f"{prefix}anomaly_rate": anomaly_count / total if total else 0.0,
        f"{prefix}packet_loss_avg": _mean(packet_losses),
        f"{prefix}offline_frequency": null_count / total if total else 0.0,
    }


def extract_features(camera_id, db_connection):
    """Extract long-term and short-term health features for one camera."""
    rows = db_connection.execute(
        """
        SELECT response_time_ms, packet_loss_pct, is_anomaly
        FROM ping_history
        WHERE camera_id = ?
        ORDER BY recorded_at DESC
        LIMIT 200
        """,
        (camera_id,),
    ).fetchall()
    rows = list(rows)
    if len(rows) < 10:
        return None
    features = _window_metrics(rows)
    recent = _window_metrics(rows[:20], "recent_")
    features["recent_instability"] = (
        recent["recent_anomaly_rate"] * 0.45
        + recent["recent_offline_frequency"] * 0.35
        + min(recent["recent_avg_latency"] / 250, 1.0) * 0.20
    )
    features.update(recent)
    return features


def feature_names():
    """Return the stable model feature order."""
    return [
        "avg_latency", "max_latency", "latency_stddev", "null_count", "anomaly_rate",
        "packet_loss_avg", "offline_frequency", "recent_instability", "recent_avg_latency",
        "recent_max_latency", "recent_latency_stddev", "recent_null_count",
        "recent_anomaly_rate", "recent_packet_loss_avg", "recent_offline_frequency",
    ]


def to_vector(features):
    """Convert a feature dictionary to the vector order expected by the models."""
    return [float(features.get(name, 0.0) or 0.0) for name in feature_names()]
