from __future__ import annotations

import argparse

from .config import CONFIG
from .hardware import detect_hardware
from .profile import select_profile
from .services import create_default_manager
from .system import get_system_info


def show_info() -> None:
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


def show_services() -> None:
    manager = create_default_manager()

    print("Edima Services")
    print()

    for service in manager.list():
        state = "enabled" if service.enabled else "disabled"
        print(
            f"{service.name:<12} "
            f"{service.service_class.value:<9} "
            f"{state:<8} "
            f"{service.description}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(prog="edima")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("info")
    subparsers.add_parser("services")

    args = parser.parse_args()

    if args.command == "services":
        show_services()
    else:
        show_info()


if __name__ == "__main__":
    main()
