"""Minimal standard-library WebSocket server for real-time dashboard updates."""

import base64
import hashlib
import socket
import threading

from websocket.connection_manager import manager

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _handshake(conn):
    request = conn.recv(4096).decode("utf-8", errors="ignore")
    headers = {}
    for line in request.split("\r\n")[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    ws_key = headers.get("sec-websocket-key")
    if not ws_key:
        return False
    accept = base64.b64encode(hashlib.sha1((ws_key + GUID).encode("utf-8")).digest()).decode("ascii")
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
    )
    conn.sendall(response.encode("utf-8"))
    return True


def _read_frame(conn):
    first = conn.recv(2)
    if len(first) < 2:
        return None
    opcode = first[0] & 0x0F
    masked = first[1] & 0x80
    length = first[1] & 0x7F
    if length == 126:
        length = int.from_bytes(conn.recv(2), "big")
    elif length == 127:
        length = int.from_bytes(conn.recv(8), "big")
    mask = conn.recv(4) if masked else b""
    payload = b""
    while len(payload) < length:
        chunk = conn.recv(length - len(payload))
        if not chunk:
            break
        payload += chunk
    if masked:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    if opcode == 0x8:
        return None
    if opcode == 0x1:
        return payload.decode("utf-8", errors="ignore")
    return ""


def _handle_client(conn):
    try:
        if not _handshake(conn):
            conn.close()
            return
        manager.add(conn)
        manager.broadcast("CAMERA_ONLINE", {"name": "WebSocket connected", "status": "ONLINE"})
        while True:
            if _read_frame(conn) is None:
                break
    except Exception:
        pass
    finally:
        manager.remove(conn)
        try:
            conn.close()
        except Exception:
            pass


def start_websocket_server(host="127.0.0.1", port=8001):
    """Start the WebSocket listener in a daemon thread."""
    def run():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, port))
            server.listen(50)
            while True:
                try:
                    conn, _addr = server.accept()
                    threading.Thread(target=_handle_client, args=(conn,), daemon=True).start()
                except Exception:
                    continue
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
