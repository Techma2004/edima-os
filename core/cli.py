from __future__ import annotations

from .config import CONFIG
from .hardware import detect_hardware
from .profile import select_profile
from .system import get_system_info


def main() -> None:
    system = get_system_info()
    hardware = detect_hardware()
    profile = select_profile(hardware)

    print(f"{CONFIG.name} {CONFIG.version}")
    print()
    print(f"Host:        {system.hostname}")
    print(f"Kernel:      {system.kernel}")
    print(f"Arch:        {system.architecture}")
    print(f"CPU threads: {hardware.cpu_threads}")
    print(f"Memory:      {hardware.memory_gib:.2f} GiB")
    print(f"GPU:         {hardware.gpu}")
    print(f"Profile:     {profile.name}")


if __name__ == "__main__":
    main()
