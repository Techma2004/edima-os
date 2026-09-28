from pathlib import Path

from shell.launcher.apps import (
    Application,
    _parse_desktop_file,
    discover_applications,
    find_application,
)


def test_parse_desktop_application(tmp_path: Path) -> None:
    desktop = tmp_path / "example.desktop"
    desktop.write_text(
        """[Desktop Entry]
Type=Application
Name=Example App
Comment=An example
Exec=example --open %U
Categories=Utility;Development;
""",
        encoding="utf-8",
    )

    application = _parse_desktop_file(desktop)

    assert application is not None
    assert application.name == "Example App"
    assert application.command == "example --open %U"
    assert application.categories == ("Utility", "Development")


def test_hidden_application_is_ignored(tmp_path: Path) -> None:
    desktop = tmp_path / "hidden.desktop"
    desktop.write_text(
        """[Desktop Entry]
Type=Application
Name=Hidden App
Exec=hidden
NoDisplay=true
""",
        encoding="utf-8",
    )

    assert _parse_desktop_file(desktop) is None


def test_find_application() -> None:
    applications = (
        Application(name="Dolphin", command="dolphin"),
        Application(name="Kate", command="kate"),
    )

    assert find_application("kate", applications).name == "Kate"
    assert find_application("missing", applications) is None


def test_discover_applications_returns_sorted_entries() -> None:
    applications = discover_applications()

    assert applications == tuple(
        sorted(applications, key=lambda app: app.name.casefold())
    )
    assert all(application.name for application in applications)
