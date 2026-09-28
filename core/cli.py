from __future__ import annotations

import argparse

from .config import CONFIG
from .hardware import detect_hardware
from .profile import select_profile
from .services import create_default_manager
from .system import get_system_info
from shell.launcher.cli import launch_application, list_applications


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


def _print_services(manager) -> None:
    manager.sync_all()

    print("Edima Services")
    print()

    for service in manager.list():
        runtime = manager.runtime(service.name)

        print(
            f"{service.name:<12} "
            f"{service.service_class.value:<9} "
            f"{service.desired_state.value:<8} "
            f"{service.startup_policy.value:<10} "
            f"{runtime.state.value:<9} "
            f"{service.description}"
        )


def show_services() -> None:
    _print_services(create_default_manager())


def show_service_status(name: str) -> None:
    manager = create_default_manager()
    runtime = manager.sync_runtime(name)
    service = manager.get(name)

    print(f"{service.name}: {runtime.state.value}")
    print(f"Class:   {service.service_class.value}")
    print(f"Policy:  {service.startup_policy.value}")

    if service.unit:
        print(f"Unit:    {service.unit}")


def control_service(name: str, action: str) -> None:
    manager = create_default_manager()
    runtime = getattr(manager, action)(name)

    print(f"{name}: {runtime.state.value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edima")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("info")

    launcher = subparsers.add_parser("launcher")
    launcher_subparsers = launcher.add_subparsers(dest="launcher_command")

    launcher_list = launcher_subparsers.add_parser("list")
    launcher_list.set_defaults(handler=lambda args: list_applications())

    launcher_launch = launcher_subparsers.add_parser("launch")
    launcher_launch.add_argument("name")
    launcher_launch.set_defaults(
        handler=lambda args: launch_application(args.name)
    )

    services = subparsers.add_parser("services")
    services.set_defaults(handler=lambda args: show_services())

    service = subparsers.add_parser("service")
    service_subparsers = service.add_subparsers(dest="service_command")

    service_list = service_subparsers.add_parser("list")
    service_list.set_defaults(handler=lambda args: show_services())

    service_status = service_subparsers.add_parser("status")
    service_status.add_argument("name")
    service_status.set_defaults(
        handler=lambda args: show_service_status(args.name)
    )

    for action in ("start", "stop", "restart"):
        command = service_subparsers.add_parser(action)
        command.add_argument("name")
        command.set_defaults(
            handler=lambda args, action=action: control_service(
                args.name, action
            )
        )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "handler"):
        try:
            args.handler(args)
        except (KeyError, ValueError) as exc:
            parser.error(str(exc))
        return

    if args.command == "info":
        show_info()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
