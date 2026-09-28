# Edima OS Architecture

## Layers

```text
Edima OS
├── Core
├── Shell
├── Services
├── Integrations
├── Developer
├── AI
├── Security
├── Themes
└── Profiles
```

## Desktop Stack

```text
Wayland
  ↓
Hyprland
  ↓
Edima Shell
  ↓
Edima Services
  ↓
Applications
```

## Design Rule

Critical desktop components must start first. Optional developer, AI, indexing, and monitoring services should start lazily or asynchronously whenever possible.
