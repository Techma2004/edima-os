from __future__ import annotations

import argparse

from .apps import discover_applications, find_application, launch
from .wofi import run_launcher


def list_applications() -> None:
    applications = discover_applications()

    print("Edima Applications")
    print()

    for application in applications:
        print(f"{application.name:<32} {application.command}")


def launch_application(name: str) -> None:
    application = find_application(name)

    if application is None:
        raise ValueError(f"Application not found: {name}")

    launch(application)
    print(f"Launched: {application.name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edima launcher")
    subparsers = parser.add_subparsers(dest="command")

    list_command = subparsers.add_parser("list")
    list_command.set_defaults(handler=lambda args: list_applications())

    run_command = subparsers.add_parser("run")
    run_command.set_defaults(handler=lambda args: run_launcher())

    launch_command = subparsers.add_parser("launch")
    launch_command.add_argument("name")
    launch_command.set_defaults(
        handler=lambda args: launch_application(args.name)
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, "handler"):
        try:
            args.handler(args)
        except ValueError as exc:
            parser.error(str(exc))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
