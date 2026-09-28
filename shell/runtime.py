from __future__ import annotations

from dataclasses import dataclass

from core.profile import HardwareProfile
from .state import ShellRuntime, ShellState


@dataclass(frozen=True)
class ShellComponent:
    name: str
    required: bool = True


DEFAULT_COMPONENTS = (
    ShellComponent("panel"),
    ShellComponent("launcher"),
    ShellComponent("notifications"),
    ShellComponent("clipboard"),
)


class ShellManager:
    def __init__(
        self,
        profile: HardwareProfile,
        components: tuple[ShellComponent, ...] = DEFAULT_COMPONENTS,
    ) -> None:
        self.profile = profile
        self.components = components
        self.runtime = ShellRuntime()

    def start(self) -> ShellRuntime:
        if self.runtime.state == ShellState.RUNNING:
            return self.runtime

        self.runtime.state = ShellState.STARTING
        self.runtime.components = tuple(
            component.name
            for component in self.components
            if self._enabled(component)
        )
        self.runtime.state = ShellState.RUNNING
        return self.runtime

    def stop(self) -> ShellRuntime:
        if self.runtime.state == ShellState.STOPPED:
            return self.runtime

        self.runtime.state = ShellState.STOPPING
        self.runtime.components = ()
        self.runtime.state = ShellState.STOPPED
        return self.runtime

    def reload(self) -> ShellRuntime:
        self.stop()
        return self.start()

    def _enabled(self, component: ShellComponent) -> bool:
        if component.required:
            return True

        return self.profile.background_services
