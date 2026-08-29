"""Classification rules that combine ICMP and RTSP camera health signals."""


def classify_health(ping_result, rtsp_result, rtsp_url):
    """Return the normalized camera health state used by the dashboard and API."""
    latency = ping_result.get("latency_ms")
    packet_loss = ping_result.get("packet_loss_pct", 100)
    stream_response = rtsp_result.get("response_ms") if rtsp_result else None
    has_rtsp = bool(rtsp_url)

    if not ping_result.get("success"):
        return {
            "status": "OFFLINE",
            "stream_status": "No ping response",
            "latency_ms": latency,
            "stream_response_ms": stream_response,
            "packet_loss_pct": packet_loss,
            "is_anomaly": 0,
        }
    if has_rtsp and rtsp_result and not rtsp_result.get("success"):
        return {
            "status": "STREAM_FAILURE",
            "stream_status": "Ping OK; RTSP stream unavailable",
            "latency_ms": latency,
            "stream_response_ms": stream_response,
            "packet_loss_pct": packet_loss,
            "is_anomaly": 1,
        }
    if latency is not None and latency > 150:
        return {
            "status": "UNSTABLE",
            "stream_status": "High latency",
            "latency_ms": latency,
            "stream_response_ms": stream_response,
            "packet_loss_pct": packet_loss,
            "is_anomaly": 1,
        }
    if has_rtsp and rtsp_result and rtsp_result.get("success"):
        stream_status = "Reachable; RTSP stream healthy"
    else:
        stream_status = "Reachable"
    return {
        "status": "ONLINE",
        "stream_status": stream_status,
        "latency_ms": latency,
        "stream_response_ms": stream_response,
        "packet_loss_pct": packet_loss,
        "is_anomaly": 0,
    }
