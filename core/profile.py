from __future__ import annotations

from dataclasses import dataclass

from .hardware import HardwareInfo


@dataclass(frozen=True)
class HardwareProfile:
    name: str
    animations: bool
    background_services: bool
    aggressive_indexing: bool


def select_profile(hw: HardwareInfo) -> HardwareProfile:
    if hw.memory_gib and hw.memory_gib <= 4:
        return HardwareProfile(
            name="low-resource",
            animations=False,
            background_services=False,
            aggressive_indexing=False,
        )

    if hw.memory_gib and hw.memory_gib >= 16:
        return HardwareProfile(
            name="power",
            animations=True,
            background_services=True,
            aggressive_indexing=True,
        )

    return HardwareProfile(
        name="normal",
        animations=True,
        background_services=True,
        aggressive_indexing=False,
    )
