"""Thread-safe registry and broadcaster for WebSocket client connections."""

import json
import threading
from datetime import datetime


class ConnectionManager:
    """Track active WebSocket connections and broadcast JSON events."""

    def __init__(self):
        self._connections = set()
        self._lock = threading.Lock()

    def add(self, conn):
        with self._lock:
            self._connections.add(conn)

    def remove(self, conn):
        with self._lock:
            self._connections.discard(conn)

    def broadcast(self, event_type, payload):
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        frame = self._encode_text_frame(json.dumps(event, ensure_ascii=False))
        with self._lock:
            connections = list(self._connections)
        for conn in connections:
            try:
                conn.sendall(frame)
            except Exception:
                self.remove(conn)

    @staticmethod
    def _encode_text_frame(message):
        data = message.encode("utf-8")
        length = len(data)
        if length < 126:
            header = bytes([0x81, length])
        elif length < 65536:
            header = bytes([0x81, 126]) + length.to_bytes(2, "big")
        else:
            header = bytes([0x81, 127]) + length.to_bytes(8, "big")
        return header + data


manager = ConnectionManager()
