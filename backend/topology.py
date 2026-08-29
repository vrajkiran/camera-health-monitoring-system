"""Network topology data assembly for the UCEK-JNTUK camera monitor."""

from datetime import datetime

from database import connect, row_to_dict


def _edge_health(status):
    if status == "OFFLINE":
        return "DOWN"
    if status in ("UNSTABLE", "STREAM_FAILURE"):
        return "DEGRADED"
    return "GOOD"


def get_topology_data():
    """Return switch, camera and link data for the topology canvas."""
    try:
        with connect() as db:
            rows = db.execute("SELECT * FROM cameras ORDER BY switch_id, id").fetchall()
            cameras = [row_to_dict(row) for row in rows]
        switches = {}
        nodes = []
        edges = []
        for camera in cameras:
            switch_id = camera.get("switch_id") or "UNKNOWN"
            switch = switches.setdefault(
                switch_id,
                {
                    "id": switch_id,
                    "type": "switch",
                    "switch_ip": camera.get("switch_ip") or "",
                    "total_cameras": 0,
                    "offline_cameras": 0,
                    "status": "ONLINE",
                },
            )
            switch["total_cameras"] += 1
            if camera.get("status") == "OFFLINE":
                switch["offline_cameras"] += 1
            nodes.append(
                {
                    "id": f"cam-{camera['id']}",
                    "type": "camera",
                    "camera_id": camera["id"],
                    "name": camera.get("name") or "Camera",
                    "location": camera.get("location") or "",
                    "ip_address": camera.get("ip_address") or "",
                    "status": camera.get("status") or "UNKNOWN",
                    "latency_ms": camera.get("latency_ms"),
                    "stream_status": camera.get("stream_status") or "",
                    "switch_id": switch_id,
                    "last_checked": camera.get("last_checked") or "",
                }
            )
            edges.append({"source": switch_id, "target": f"cam-{camera['id']}", "health": _edge_health(camera.get("status"))})
        probable = []
        for switch in switches.values():
            if switch["total_cameras"] and switch["offline_cameras"] == switch["total_cameras"]:
                switch["status"] = "OFFLINE"
                if switch["total_cameras"] > 1:
                    probable.append(switch["id"])
        return {
            "nodes": list(switches.values()) + nodes,
            "edges": edges,
            "probable_switch_failures": probable,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as exc:
        return {"nodes": [], "edges": [], "probable_switch_failures": [], "generated_at": datetime.now().isoformat(timespec="seconds"), "error": str(exc)}
