from core.profile import HardwareProfile
from shell.runtime import ShellComponent, ShellManager
from shell.state import ShellState


def low_resource_profile() -> HardwareProfile:
    return HardwareProfile(
        name="low-resource",
        animations=False,
        background_services=False,
        aggressive_indexing=False,
    )


def normal_profile() -> HardwareProfile:
    return HardwareProfile(
        name="normal",
        animations=True,
        background_services=True,
        aggressive_indexing=False,
    )


def test_shell_starts_required_components() -> None:
    manager = ShellManager(low_resource_profile())

    runtime = manager.start()

    assert runtime.state == ShellState.RUNNING
    assert runtime.components == (
        "panel",
        "launcher",
        "notifications",
        "clipboard",
    )


def test_shell_stops_cleanly() -> None:
    manager = ShellManager(low_resource_profile())
    manager.start()

    runtime = manager.stop()

    assert runtime.state == ShellState.STOPPED
    assert runtime.components == ()


def test_shell_reload() -> None:
    manager = ShellManager(low_resource_profile())
    manager.start()

    runtime = manager.reload()

    assert runtime.state == ShellState.RUNNING
    assert runtime.components


def test_optional_components_follow_profile() -> None:
    optional = ShellComponent("monitoring", required=False)

    low = ShellManager(low_resource_profile(), (optional,))
    normal = ShellManager(normal_profile(), (optional,))

    assert low.start().components == ()
    assert normal.start().components == ("monitoring",)


def test_start_is_idempotent() -> None:
    manager = ShellManager(low_resource_profile())

    first = manager.start()
    second = manager.start()

    assert first is second
    assert second.state == ShellState.RUNNING
