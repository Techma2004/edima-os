from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .systemd import SystemdUser


class ServiceClass(StrEnum):
    CRITICAL = "critical"
    SYSTEM = "system"
    OPTIONAL = "optional"


class DesiredState(StrEnum):
    AUTO = "auto"
    STARTED = "started"
    STOPPED = "stopped"


class RuntimeState(StrEnum):
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    FAILED = "failed"
    UNKNOWN = "unknown"


class StartupPolicy(StrEnum):
    IMMEDIATE = "immediate"
    LAZY = "lazy"
    ON_DEMAND = "on-demand"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Service:
    name: str
    description: str
    service_class: ServiceClass
    unit: str | None = None
    desired_state: DesiredState = DesiredState.AUTO
    startup_policy: StartupPolicy = StartupPolicy.IMMEDIATE
    dependencies: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class ServiceRuntime:
    state: RuntimeState = RuntimeState.UNKNOWN
    healthy: bool | None = None


class ServiceManager:
    def __init__(self) -> None:
        self._services: dict[str, Service] = {}
        self._runtime: dict[str, ServiceRuntime] = {}

    def register(self, service: Service) -> None:
        if service.name in self._services:
            raise ValueError(f"Service already registered: {service.name}")

        self._services[service.name] = service
        self._runtime[service.name] = ServiceRuntime()

    def get(self, name: str) -> Service:
        try:
            return self._services[name]
        except KeyError:
            raise KeyError(f"Unknown service: {name}") from None

    def runtime(self, name: str) -> ServiceRuntime:
        try:
            return self._runtime[name]
        except KeyError:
            raise KeyError(f"Unknown service: {name}") from None

    def dependencies(self, name: str) -> tuple[Service, ...]:
        service = self.get(name)

        dependencies: list[Service] = []
        for dependency in service.dependencies:
            dependencies.append(self.get(dependency))

        return tuple(dependencies)

    def list(self) -> tuple[Service, ...]:
        order = {
            ServiceClass.CRITICAL: 0,
            ServiceClass.SYSTEM: 1,
            ServiceClass.OPTIONAL: 2,
        }

        return tuple(
            sorted(
                self._services.values(),
                key=lambda service: (order[service.service_class], service.name),
            )
        )

    def sync_runtime(self, name: str) -> ServiceRuntime:
        service = self.get(name)

        if service.unit is None:
            return self.runtime(name)

        systemd = SystemdUser.status(service.unit)

        state_map = {
            "active": RuntimeState.ACTIVE,
            "failed": RuntimeState.FAILED,
            "inactive": RuntimeState.INACTIVE,
            "activating": RuntimeState.STARTING,
            "deactivating": RuntimeState.STOPPING,
        }

        runtime = self.runtime(name)
        runtime.state = state_map.get(systemd.state, RuntimeState.UNKNOWN)
        runtime.healthy = (
            True if runtime.state == RuntimeState.ACTIVE
            else False if runtime.state == RuntimeState.FAILED
            else None
        )

        return runtime

    def sync_all(self) -> None:
        for service in self._services.values():
            self.sync_runtime(service.name)

    def _control(self, name: str, action: str) -> ServiceRuntime:
        service = self.get(name)

        if service.unit is None:
            raise ValueError(f"Service has no systemd unit: {name}")

        if action == "start":
            success = SystemdUser.start(service.unit)
        elif action == "stop":
            success = SystemdUser.stop(service.unit)
        elif action == "restart":
            success = SystemdUser.restart(service.unit)
        else:
            raise ValueError(f"Unsupported service action: {action}")

        self.sync_runtime(name)

        if not success and self.runtime(name).state != RuntimeState.ACTIVE:
            self.runtime(name).healthy = False

        return self.runtime(name)

    def start(self, name: str) -> ServiceRuntime:
        return self._start(name, set())

    def _start(self, name: str, visiting: set[str]) -> ServiceRuntime:
        if name in visiting:
            raise ValueError(f"Service dependency cycle detected: {name}")

        visiting.add(name)

        for dependency in self.dependencies(name):
            self.sync_runtime(dependency.name)
            dependency_runtime = self.runtime(dependency.name)

            if dependency_runtime.state != RuntimeState.ACTIVE:
                self._start(dependency.name, visiting)

        visiting.remove(name)
        return self._control(name, "start")

    def stop(self, name: str) -> ServiceRuntime:
        return self._control(name, "stop")

    def restart(self, name: str) -> ServiceRuntime:
        return self._control(name, "restart")


def create_default_manager() -> ServiceManager:
    manager = ServiceManager()

    manager.register(
        Service(
            name="hyprland",
            description="Wayland compositor",
            service_class=ServiceClass.CRITICAL,
            unit="hyprland.service",
            startup_policy=StartupPolicy.IMMEDIATE,
        )
    )

    manager.register(
        Service(
            name="network",
            description="Network management",
            service_class=ServiceClass.SYSTEM,
            unit="NetworkManager.service",
            startup_policy=StartupPolicy.IMMEDIATE,
        )
    )

    manager.register(
        Service(
            name="audio",
            description="Audio system",
            service_class=ServiceClass.SYSTEM,
            startup_policy=StartupPolicy.IMMEDIATE,
        )
    )

    manager.register(
        Service(
            name="bluetooth",
            description="Bluetooth management",
            service_class=ServiceClass.SYSTEM,
            unit="bluetooth.service",
            startup_policy=StartupPolicy.ON_DEMAND,
        )
    )

    manager.register(
        Service(
            name="kdeconnect",
            description="Device integration",
            service_class=ServiceClass.OPTIONAL,
            unit="kdeconnect.service",
            startup_policy=StartupPolicy.LAZY,
            dependencies=("network",),
        )
    )

    manager.register(
        Service(
            name="sally",
            description="Local AI assistant",
            service_class=ServiceClass.OPTIONAL,
            startup_policy=StartupPolicy.LAZY,
            dependencies=("network",),
        )
    )

    return manager
