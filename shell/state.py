from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ShellState(StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    DEGRADED = "degraded"


@dataclass
class ShellRuntime:
    state: ShellState = ShellState.STOPPED
    components: tuple[str, ...] = ()
