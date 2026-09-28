from core.services import (
    DesiredState,
    RuntimeState,
    Service,
    ServiceClass,
    ServiceManager,
    StartupPolicy,
    create_default_manager,
)


def test_register_and_lookup() -> None:
    manager = ServiceManager()

    service = Service(
        name="test",
        description="Test service",
        service_class=ServiceClass.OPTIONAL,
    )

    manager.register(service)

    assert manager.get("test") == service
    assert manager.runtime("test").state == RuntimeState.UNKNOWN


def test_duplicate_registration_fails() -> None:
    manager = ServiceManager()

    service = Service(
        name="test",
        description="Test service",
        service_class=ServiceClass.OPTIONAL,
    )

    manager.register(service)

    try:
        manager.register(service)
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("Expected duplicate registration to fail")


def test_dependencies_are_resolved() -> None:
    manager = create_default_manager()

    dependencies = manager.dependencies("sally")

    assert tuple(service.name for service in dependencies) == ("network",)


def test_missing_dependency_fails_on_resolution() -> None:
    manager = ServiceManager()

    manager.register(
        Service(
            name="broken",
            description="Broken service",
            service_class=ServiceClass.OPTIONAL,
            dependencies=("missing",),
        )
    )

    try:
        manager.dependencies("broken")
    except KeyError as exc:
        assert "Unknown service: missing" in str(exc)
    else:
        raise AssertionError("Expected missing dependency to fail")


def test_default_startup_policies() -> None:
    manager = create_default_manager()

    assert manager.get("hyprland").startup_policy == StartupPolicy.IMMEDIATE
    assert manager.get("bluetooth").startup_policy == StartupPolicy.ON_DEMAND
    assert manager.get("sally").startup_policy == StartupPolicy.LAZY


def test_default_desired_state_is_auto() -> None:
    manager = create_default_manager()

    assert manager.get("sally").desired_state == DesiredState.AUTO


def test_service_order() -> None:
    manager = create_default_manager()

    names = tuple(service.name for service in manager.list())

    assert names[:1] == ("hyprland",)
    assert names.index("network") < names.index("sally")


def test_sync_runtime_maps_active_systemd_state() -> None:
    manager = create_default_manager()

    class FakeSystemd:
        state = "active"

    from unittest.mock import patch

    with patch("core.services.SystemdUser.status", return_value=FakeSystemd()):
        runtime = manager.sync_runtime("hyprland")

    assert runtime.state == RuntimeState.ACTIVE
    assert runtime.healthy is True


def test_sync_runtime_maps_failed_systemd_state() -> None:
    manager = create_default_manager()

    class FakeSystemd:
        state = "failed"

    from unittest.mock import patch

    with patch("core.services.SystemdUser.status", return_value=FakeSystemd()):
        runtime = manager.sync_runtime("hyprland")

    assert runtime.state == RuntimeState.FAILED
    assert runtime.healthy is False


def test_sync_runtime_keeps_unitless_service_unknown() -> None:
    manager = create_default_manager()

    runtime = manager.sync_runtime("audio")

    assert runtime.state == RuntimeState.UNKNOWN
    assert runtime.healthy is None


def test_start_requires_systemd_unit() -> None:
    manager = create_default_manager()

    try:
        manager.start("audio")
    except ValueError as exc:
        assert "no systemd unit" in str(exc)
    else:
        raise AssertionError("Expected unitless service start to fail")


def test_start_respects_dependencies() -> None:
    manager = create_default_manager()

    from unittest.mock import patch

    calls: list[str] = []

    def fake_start(unit: str) -> bool:
        calls.append(unit)
        return True

    def fake_status(unit: str):
        class FakeRuntime:
            state = "active"
            sub_state = "running"
            active = True
            failed = False

        return FakeRuntime()

    with patch("core.services.SystemdUser.start", side_effect=fake_start):
        with patch("core.services.SystemdUser.status", side_effect=fake_status):
            manager.start("kdeconnect")

    assert calls == [
        "NetworkManager.service",
        "kdeconnect.service",
    ]
