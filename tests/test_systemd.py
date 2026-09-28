from __future__ import annotations

from unittest.mock import patch

from core.systemd import SystemdUser


def test_systemd_status_active() -> None:
    completed = type(
        "Completed",
        (),
        {
            "returncode": 0,
            "stdout": (
                "ActiveState=active\n"
                "SubState=running\n"
                "UnitFileState=enabled\n"
            ),
        },
    )()

    with patch("core.systemd.subprocess.run", return_value=completed):
        status = SystemdUser.status("example.service")

    assert status.state == "active"
    assert status.sub_state == "running"
    assert status.active is True
    assert status.failed is False


def test_systemd_status_failed() -> None:
    completed = type(
        "Completed",
        (),
        {
            "returncode": 3,
            "stdout": (
                "ActiveState=failed\n"
                "SubState=failed\n"
            ),
        },
    )()

    with patch("core.systemd.subprocess.run", return_value=completed):
        status = SystemdUser.status("example.service")

    assert status.state == "unknown"
    assert status.sub_state == "unknown"
    assert status.active is False
    assert status.failed is False


def test_systemd_status_unknown_unit() -> None:
    completed = type(
        "Completed",
        (),
        {
            "returncode": 5,
            "stdout": "",
        },
    )()

    with patch("core.systemd.subprocess.run", return_value=completed):
        status = SystemdUser.status("missing.service")

    assert status.state == "unknown"
    assert status.sub_state == "unknown"
    assert status.active is False
    assert status.failed is False


def test_systemd_start() -> None:
    with patch("core.systemd.subprocess.run") as run:
        run.return_value = type(
            "Completed",
            (),
            {"returncode": 0, "stdout": ""},
        )()

        assert SystemdUser.start("example.service") is True

        args = run.call_args.args[0]
        assert args[:4] == [
            "systemctl",
            "--user",
            "start",
            "example.service",
        ]


def test_systemd_stop() -> None:
    with patch("core.systemd.subprocess.run") as run:
        run.return_value = type(
            "Completed",
            (),
            {"returncode": 0, "stdout": ""},
        )()

        assert SystemdUser.stop("example.service") is True


def test_systemd_restart() -> None:
    with patch("core.systemd.subprocess.run") as run:
        run.return_value = type(
            "Completed",
            (),
            {"returncode": 0, "stdout": ""},
        )()

        assert SystemdUser.restart("example.service") is True
