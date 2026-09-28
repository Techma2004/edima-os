from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Application:
    name: str
    command: str
    desktop_file: Path | None = None
    comment: str = ""
    categories: tuple[str, ...] = ()


def _desktop_dirs() -> tuple[Path, ...]:
    dirs = [
        Path.home() / ".local/share/applications",
        Path("/usr/local/share/applications"),
        Path("/usr/share/applications"),
    ]

    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        dirs.insert(0, Path(data_home) / "applications")

    return tuple(dict.fromkeys(dirs))


def _value(lines: list[str], key: str) -> str:
    prefix = f"{key}="
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def _is_hidden(lines: list[str]) -> bool:
    return _value(lines, "NoDisplay").lower() == "true" or _value(
        lines, "Hidden"
    ).lower() == "true"


def _parse_desktop_file(path: Path) -> Application | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None

    if _value(lines, "Type") != "Application" or _is_hidden(lines):
        return None

    name = _value(lines, "Name")
    command = _value(lines, "Exec")

    if not name or not command:
        return None

    return Application(
        name=name,
        command=command,
        desktop_file=path,
        comment=_value(lines, "Comment"),
        categories=tuple(
            category
            for category in _value(lines, "Categories").split(";")
            if category
        ),
    )


def discover_applications() -> tuple[Application, ...]:
    applications: dict[str, Application] = {}

    for directory in _desktop_dirs():
        if not directory.is_dir():
            continue

        for path in directory.glob("*.desktop"):
            application = _parse_desktop_file(path)
            if application is not None:
                applications.setdefault(application.name.lower(), application)

    return tuple(sorted(applications.values(), key=lambda app: app.name.lower()))


def find_application(
    name: str,
    applications: tuple[Application, ...] | None = None,
) -> Application | None:
    target = name.casefold()

    for application in applications or discover_applications():
        if application.name.casefold() == target:
            return application

    return None


def launch(application: Application) -> subprocess.Popen[bytes]:
    command = application.command

    # Desktop Exec fields are not shell commands. Remove common field codes
    # before launching so applications receive no accidental file arguments.
    command = " ".join(
        token
        for token in shlex.split(command)
        if not token.startswith("%")
    )

    return subprocess.Popen(
        shlex.split(command),
        start_new_session=True,
    )
