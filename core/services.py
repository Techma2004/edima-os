from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ServiceClass(StrEnum):
    CRITICAL = "critical"
    SYSTEM = "system"
    OPTIONAL = "optional"


class ServiceState(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Service:
    name: str
    description: str
    service_class: ServiceClass
    unit: str | None = None
    enabled: bool = True


class ServiceManager:
    def __init__(self) -> None:
        self._services: dict[str, Service] = {}

    def register(self, service: Service) -> None:
        if service.name in self._services:
            raise ValueError(f"Service already registered: {service.name}")

        self._services[service.name] = service

    def get(self, name: str) -> Service:
        try:
            return self._services[name]
        except KeyError:
            raise KeyError(f"Unknown service: {name}") from None

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


def create_default_manager() -> ServiceManager:
    manager = ServiceManager()

    manager.register(
        Service(
            name="hyprland",
            description="Wayland compositor",
            service_class=ServiceClass.CRITICAL,
            unit="hyprland.service",
        )
    )

    manager.register(
        Service(
            name="network",
            description="Network management",
            service_class=ServiceClass.SYSTEM,
            unit="NetworkManager.service",
        )
    )

    manager.register(
        Service(
            name="audio",
            description="Audio system",
            service_class=ServiceClass.SYSTEM,
        )
    )

    manager.register(
        Service(
            name="bluetooth",
            description="Bluetooth management",
            service_class=ServiceClass.SYSTEM,
            unit="bluetooth.service",
        )
    )

    manager.register(
        Service(
            name="kdeconnect",
            description="Device integration",
            service_class=ServiceClass.OPTIONAL,
            unit="kdeconnect.service",
        )
    )

    manager.register(
        Service(
            name="sally",
            description="Local AI assistant",
            service_class=ServiceClass.OPTIONAL,
        )
    )

    return manager
