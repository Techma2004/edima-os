# Edima OS

A lightweight, developer-first Linux desktop environment built on Debian and Hyprland.

## Vision

Edima OS is a modular, fast, hardware-aware workstation environment designed around keyboard-first workflows, developer tooling, and native SALLY integration.

## Status

🚧 Early development — Edima OS v0.1

## Architecture

- **Core** — configuration, IPC, hardware detection, process management
- **Shell** — panel, launcher, workspaces, control center
- **Services** — notifications, clipboard, screenshots, wallpaper, media, power, network
- **Integrations** — KDE Connect, Git, projects, terminal
- **Developer** — development environment and project tooling
- **AI** — SALLY and local AI integration
- **Security** — system health and security tooling
- **Themes** — Edima visual system
- **Profiles** — hardware-aware configurations

## Principles

1. Fast boot
2. Low idle memory
3. Minimal background processes
4. Modular architecture
5. Keyboard-first workflow
6. Developer-first experience
7. Hardware awareness
8. Reproducible configuration
9. Secure defaults
10. No unnecessary bloat

## Desktop

Hyprland is the primary Wayland compositor.

## Development

Edima OS is developed incrementally on Debian before eventually becoming independently reproducible.
