"""LAN IP detection without extra dependencies."""
from __future__ import annotations

import socket


def get_lan_ip() -> str | None:
    """Return the primary IPv4 address used for outbound traffic, or None."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None
