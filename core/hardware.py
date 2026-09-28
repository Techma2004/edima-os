from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HardwareInfo:
    cpu_threads: int
    memory_gib: float
    architecture: str
    gpu: str


GPU_VENDORS = {
    "0x8086": "Intel",
    "0x1002": "AMD",
    "0x10de": "NVIDIA",
}


def _memory_gib() -> float:
    try:
        mem_kib = int(
            Path("/proc/meminfo").read_text().split("MemTotal:")[1].split()[0]
        )
        return round(mem_kib / 1024 / 1024, 2)
    except (OSError, IndexError, ValueError):
        return 0.0


def _gpu() -> str:
    drm = Path("/sys/class/drm")
    if not drm.exists():
        return "Unknown"

    vendors: set[str] = set()

    for card in drm.glob("card*/device/vendor"):
        try:
            vendor_id = card.read_text().strip().lower()
            vendors.add(GPU_VENDORS.get(vendor_id, vendor_id))
        except OSError:
            continue

    return ", ".join(sorted(vendors)) or "Unknown"


def detect_hardware() -> HardwareInfo:
    return HardwareInfo(
        cpu_threads=os.cpu_count() or 1,
        memory_gib=_memory_gib(),
        architecture=platform.machine(),
        gpu=_gpu(),
    )
