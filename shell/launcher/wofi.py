from __future__ import annotations

import os
import subprocess
from pathlib import Path


CSS = Path(__file__).with_name("edima.css")


def run_launcher() -> None:
    environment = os.environ.copy()
    environment["GDK_BACKEND"] = "wayland"
    environment["GTK_THEME"] = "Adwaita:dark"

    subprocess.run(
        [
            "wofi",
            "--show",
            "drun",
            "--allow-images",
            "--insensitive",
            "--allow-markup",
            "--prompt",
            "Launch",
            "--width",
            "520",
            "--height",
            "520",
            "--cache-file",
            "/dev/null",
            "--style",
            str(CSS),
        ],
        check=False,
        env=environment,
    )


if __name__ == "__main__":
    run_launcher()
