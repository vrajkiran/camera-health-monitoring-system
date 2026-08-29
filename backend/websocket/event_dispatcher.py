"""Dispatch camera and alert events to connected WebSocket clients."""

from websocket.connection_manager import manager


VALID_EVENT_TYPES = {"CAMERA_ONLINE", "CAMERA_OFFLINE", "STREAM_FAILURE", "STREAM_RECOVERED", "ALERT_CREATED"}


def dispatch(event_type, data):
    """Broadcast a typed event if it is part of the real-time event contract."""
    if event_type not in VALID_EVENT_TYPES:
        return
    manager.broadcast(event_type, data)
