from __future__ import annotations

import platform
import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class SystemInfo:
    hostname: str
    kernel: str
    architecture: str
    python: str


def get_system_info() -> SystemInfo:
    return SystemInfo(
        hostname=socket.gethostname(),
        kernel=platform.release(),
        architecture=platform.machine(),
        python=platform.python_version(),
    )
