"""AI diagnosis feedback service."""

from datetime import datetime
from database import connect, row_to_dict


def now_text():
    return datetime.now().isoformat(timespec="seconds")


class AIFeedbackService:
    def submit(self, incident_id, diagnosis_correct, operator, actual_cause=None, resolution_notes=""):
        created = now_text()
        with connect() as db:
            incident = db.execute("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,)).fetchone()
            if not incident:
                raise ValueError("Incident not found")
            db.execute(
                """
                INSERT INTO ai_feedback
                (incident_id, camera_id, predicted_cause, actual_cause, diagnosis_correct, resolution_notes, operator, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (incident_id, incident["camera_id"], incident["diagnosis"], actual_cause, 1 if diagnosis_correct else 0, resolution_notes, operator, created),
            )
            db.execute("INSERT INTO user_activity (action, description, created_at) VALUES (?, ?, ?)", ("AI_FEEDBACK_SUBMITTED", f"AI feedback submitted for incident {incident_id} by {operator}.", created))
        return {"ok": True, "incident_id": incident_id}

    def performance(self):
        with connect() as db:
            rows = [row_to_dict(row) for row in db.execute("SELECT * FROM ai_feedback ORDER BY created_at DESC").fetchall()]
        total = len(rows)
        correct = sum(1 for row in rows if row["diagnosis_correct"])
        incorrect = total - correct
        by_predicted = {}
        confusion = {}
        monthly = {}
        for row in rows:
            predicted = row["predicted_cause"] or "Unknown"
            actual = row["actual_cause"] or (predicted if row["diagnosis_correct"] else "Unspecified")
            if not row["diagnosis_correct"]:
                by_predicted[predicted] = by_predicted.get(predicted, 0) + 1
            confusion.setdefault(predicted, {})[actual] = confusion.setdefault(predicted, {}).get(actual, 0) + 1
            month = (row["created_at"] or "")[:7]
            monthly.setdefault(month, {"total": 0, "correct": 0})
            monthly[month]["total"] += 1
            monthly[month]["correct"] += 1 if row["diagnosis_correct"] else 0
        return {
            "diagnosis_accuracy": round((correct / total * 100), 2) if total else None,
            "total_predictions": total,
            "correct_predictions": correct,
            "incorrect_predictions": incorrect,
            "feedback_count": total,
            "most_incorrect_predictions": sorted(by_predicted.items(), key=lambda item: item[1], reverse=True)[:10],
            "confusion_matrix": confusion,
            "root_cause_prediction_accuracy": round((correct / total * 100), 2) if total else None,
            "monthly_accuracy_trend": [{"month": month, "accuracy": round(v["correct"] / v["total"] * 100, 2) if v["total"] else None, **v} for month, v in sorted(monthly.items())],
        }

    def list_feedback(self):
        with connect() as db:
            return [row_to_dict(row) for row in db.execute("SELECT * FROM ai_feedback ORDER BY created_at DESC LIMIT 300").fetchall()]
