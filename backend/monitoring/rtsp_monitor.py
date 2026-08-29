"""Lightweight RTSP port health checks without third-party dependencies."""

import socket
import time
from urllib.parse import urlparse


def check_rtsp(rtsp_url):
    """Validate that the RTSP endpoint port accepts TCP connections."""
    if not rtsp_url:
        return {"success": False, "response_ms": None, "error": "No RTSP URL configured"}
    try:
        parsed = urlparse(rtsp_url)
        host = parsed.hostname
        port = parsed.port or 554
        if not host:
            return {"success": False, "response_ms": None, "error": "Invalid RTSP URL"}
        started = time.perf_counter()
        with socket.create_connection((host, port), timeout=3):
            elapsed = int((time.perf_counter() - started) * 1000)
        return {"success": True, "response_ms": elapsed, "error": None}
    except Exception as exc:
        return {"success": False, "response_ms": None, "error": str(exc) or "RTSP connection failed"}
