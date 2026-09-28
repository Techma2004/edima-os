from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EdimaConfig:
    name: str = "Edima OS"
    version: str = "0.1.0"
    config_dir: Path = Path.home() / ".config" / "edima"
    profile: str = "auto"


CONFIG = EdimaConfig()
