"""Platform-aware ICMP ping health checks for registered CCTV cameras."""

import platform
import re
import subprocess


def _offline():
    return {"success": False, "latency_ms": None, "packet_loss_pct": 100}


def run_ping(ip_address):
    """Run one ICMP ping and return success, latency and packet loss."""
    if not ip_address:
        return _offline()
    try:
        if platform.system().lower().startswith("win"):
            command = ["ping", "-n", "1", "-w", "1000", ip_address]
        else:
            command = ["ping", "-c", "1", "-W", "1", ip_address]
        result = subprocess.run(command, capture_output=True, text=True, timeout=3)
        output = f"{result.stdout}\n{result.stderr}"
        if result.returncode != 0:
            return _offline()
        match = re.search(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
        latency = int(float(match.group(1))) if match else 1
        loss_match = re.search(r"(\d+)\s*%\s*loss", output, re.IGNORECASE)
        packet_loss = int(loss_match.group(1)) if loss_match else 0
        return {"success": True, "latency_ms": latency, "packet_loss_pct": packet_loss}
    except Exception:
        return _offline()
