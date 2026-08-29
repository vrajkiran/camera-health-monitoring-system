"""Rule-based diagnosis and recommendation engine for camera health events."""

from __future__ import annotations

RECOMMENDATIONS = {
    "Power Failure": [
        "Verify power availability at the camera endpoint.",
        "Inspect the camera power adapter or PoE injector.",
        "Check camera power LED status and replace the power source if required.",
    ],
    "PoE Failure": [
        "Verify PoE output on the connected switch port.",
        "Inspect the switch PoE budget and port power state.",
        "Check Ethernet cable continuity and camera LED activity.",
    ],
    "Switch Port Failure": [
        "Move the camera to a known working switch port for confirmation.",
        "Inspect port link status, errors and administrative shutdown state.",
        "Replace or reconfigure the affected switch port if link does not recover.",
    ],
    "Ethernet Cable Failure": [
        "Inspect both cable ends for loose or damaged connectors.",
        "Test cable continuity with a network cable tester.",
        "Replace the cable if packet loss or link instability continues.",
    ],
    "Camera Hardware Failure": [
        "Power-cycle the camera and verify boot indicators.",
        "Check camera temperature, physical damage and local power state.",
        "Replace the camera if it remains unreachable on a verified port and cable.",
    ],
    "Camera Firmware Failure": [
        "Reboot the camera and verify firmware health from the vendor utility.",
        "Check for repeated service crashes or abnormal reboot behavior.",
        "Upgrade or reinstall firmware during an approved maintenance window.",
    ],
    "RTSP Service Failure": [
        "Verify the RTSP URL, port and stream path.",
        "Confirm the camera video service is enabled and responding.",
        "Restart the camera stream service or reboot the camera if the network is reachable.",
    ],
    "Authentication Failure": [
        "Verify camera username and password used by the monitoring system.",
        "Check whether credentials were rotated or the account is locked.",
        "Update stored RTSP credentials through the authorized backend configuration path.",
    ],
    "IP Conflict": [
        "Check ARP table changes for duplicate MAC addresses.",
        "Reserve the camera IP address in DHCP or assign a unique static address.",
        "Confirm the camera responds consistently from the expected MAC address.",
    ],
    "High Packet Loss": [
        "Inspect cable quality and switch interface error counters.",
        "Check for congestion on the uplink or access switch.",
        "Replace faulty cabling or move the camera to a stable switch port.",
    ],
    "High Latency": [
        "Review switch utilization and uplink congestion.",
        "Check camera network path for intermittent packet delay.",
        "Prioritize surveillance traffic or isolate the camera VLAN if required.",
    ],
    "Unknown Failure": [
        "Validate power, network link, camera hardware and RTSP service in sequence.",
        "Review recent switch logs and camera event records.",
        "Escalate to network operations if the condition persists after basic checks.",
    ],
}

SEVERITY_BY_DIAGNOSIS = {
    "Power Failure": "CRITICAL",
    "PoE Failure": "CRITICAL",
    "Switch Port Failure": "HIGH",
    "Ethernet Cable Failure": "HIGH",
    "Camera Hardware Failure": "CRITICAL",
    "Camera Firmware Failure": "HIGH",
    "RTSP Service Failure": "HIGH",
    "Authentication Failure": "HIGH",
    "IP Conflict": "HIGH",
    "High Packet Loss": "MEDIUM",
    "High Latency": "MEDIUM",
    "Unknown Failure": "MEDIUM",
}


def recommendation_text(diagnosis: str) -> str:
    return "\n".join(f"- {item}" for item in RECOMMENDATIONS.get(diagnosis, RECOMMENDATIONS["Unknown Failure"]))


def diagnose_camera(camera: dict, health: dict | None = None) -> dict:
    """Return a professional root-cause diagnosis from camera and health signals."""
    health = health or {}
    status = health.get("status") or camera.get("status")
    latency = health.get("latency_ms", camera.get("latency_ms"))
    packet_loss = health.get("packet_loss_pct", 0)
    stream_status = str(health.get("stream_status") or camera.get("stream_status") or "")
    rtsp_url = str(camera.get("rtsp_url") or "")

    diagnosis = "Unknown Failure"
    confidence = 55

    lower_stream = stream_status.lower()
    if status == "OFFLINE":
        if packet_loss >= 100 and camera.get("switch_ip"):
            diagnosis, confidence = "PoE Failure", 82
        elif packet_loss >= 100:
            diagnosis, confidence = "Power Failure", 78
        else:
            diagnosis, confidence = "Ethernet Cable Failure", 68
    elif status == "STREAM_FAILURE":
        if "auth" in lower_stream or "401" in lower_stream or "403" in lower_stream:
            diagnosis, confidence = "Authentication Failure", 86
        elif not rtsp_url:
            diagnosis, confidence = "RTSP Service Failure", 88
        elif "firmware" in lower_stream:
            diagnosis, confidence = "Camera Firmware Failure", 72
        else:
            diagnosis, confidence = "RTSP Service Failure", 84
    elif status == "UNSTABLE":
        if packet_loss and packet_loss >= 20:
            diagnosis, confidence = "High Packet Loss", 83
        elif latency is not None and latency >= 150:
            diagnosis, confidence = "High Latency", 81
        else:
            diagnosis, confidence = "Switch Port Failure", 62
    elif latency is not None and latency >= 150:
        diagnosis, confidence = "High Latency", 76

    return {
        "diagnosis": diagnosis,
        "confidence": confidence,
        "severity": SEVERITY_BY_DIAGNOSIS.get(diagnosis, "MEDIUM"),
        "recommended_solution": recommendation_text(diagnosis),
    }
