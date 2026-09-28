from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version as package_version
from pathlib import Path


@dataclass(frozen=True)
class EdimaConfig:
    name: str = "Edima OS"
    version: str = package_version("edima-os")
    config_dir: Path = Path.home() / ".config" / "edima"
    profile: str = "auto"


CONFIG = EdimaConfig()
