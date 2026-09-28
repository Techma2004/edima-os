from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class SystemdRuntime:
    state: str
    sub_state: str
    active: bool
    failed: bool


class SystemdUser:
    """Interface to the user's systemd instance."""

    @staticmethod
    def _run(action: str, unit: str) -> bool:
        result = subprocess.run(
            [
                "systemctl",
                "--user",
                action,
                unit,
                "--no-pager",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    @staticmethod
    def status(unit: str) -> SystemdRuntime:
        result = subprocess.run(
            [
                "systemctl",
                "--user",
                "show",
                unit,
                "--property=ActiveState",
                "--property=SubState",
                "--property=UnitFileState",
                "--no-pager",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return SystemdRuntime(
                state="unknown",
                sub_state="unknown",
                active=False,
                failed=False,
            )

        values: dict[str, str] = {}

        for line in result.stdout.splitlines():
            key, separator, value = line.partition("=")
            if separator:
                values[key] = value

        state = values.get("ActiveState", "unknown")
        sub_state = values.get("SubState", "unknown")

        return SystemdRuntime(
            state=state,
            sub_state=sub_state,
            active=state == "active",
            failed=state == "failed",
        )

    @classmethod
    def start(cls, unit: str) -> bool:
        return cls._run("start", unit)

    @classmethod
    def stop(cls, unit: str) -> bool:
        return cls._run("stop", unit)

    @classmethod
    def restart(cls, unit: str) -> bool:
        return cls._run("restart", unit)
