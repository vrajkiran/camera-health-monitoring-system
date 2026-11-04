"""Shared camera health probe used by create/update and the monitor tick."""

import random

from config import DEMO_MODE
from monitoring.health_classifier import classify_health
from monitoring.ping_monitor import run_ping
from monitoring.rtsp_monitor import check_rtsp


def camera_uses_simulated_probe(camera):
    """SIMULATED always fakes; LIVE always probes; empty inherits DEMO_MODE."""
    raw = str((camera or {}).get("probe_mode") or "").strip().upper()
    if raw == "SIMULATED":
        return True
    if raw == "LIVE":
        return False
    return bool(DEMO_MODE)


def _demo_ping(camera):
    if camera.get("status") == "OFFLINE" and random.random() < 0.7:
        return {"success": False, "latency_ms": None, "packet_loss_pct": 100}
    camera_id = int(camera.get("id") or 0)
    base = 18 + camera_id * 4
    jitter = random.randint(0, 170 if camera_id in (2, 6) else 35)
    latency = base + jitter
    return {"success": True, "latency_ms": latency, "packet_loss_pct": 10 if latency > 155 else 0}


def _demo_rtsp(camera, rtsp_url, ping_result):
    if not rtsp_url:
        return {"success": False, "response_ms": None, "error": "No RTSP URL configured"}
    if not ping_result.get("success"):
        return {"success": False, "response_ms": None, "error": "Camera unreachable"}
    if int(camera.get("id") or 0) == 3 and random.random() < 0.35:
        return {"success": False, "response_ms": None, "error": "RTSP port unavailable"}
    return {"success": True, "response_ms": random.randint(24, 95), "error": None}


def probe_camera(camera):
    """Run the same ICMP + TCP-554 check for API writes and the scheduler."""
    camera = camera or {}
    ip_address = camera.get("ip_address") or ""
    rtsp_url = camera.get("rtsp_url") or ""
    if camera_uses_simulated_probe(camera):
        ping_result = _demo_ping(camera)
        rtsp_result = _demo_rtsp(camera, rtsp_url, ping_result)
    else:
        ping_result = run_ping(ip_address)
        rtsp_result = check_rtsp(rtsp_url)
    return classify_health(ping_result, rtsp_result, rtsp_url)
