#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="$ROOT_DIR/install"
MANIFEST_DIR="$INSTALL_DIR/manifests"
PROFILE_DIR="$INSTALL_DIR/profiles"

PROFILE="standard"
DRY_RUN=0
EDIMA_USER="${SUDO_USER:-${USER:-}}"

if [[ -z "$EDIMA_USER" || "$EDIMA_USER" == "root" ]]; then
    EDIMA_USER="$(logname 2>/dev/null || true)"
fi

[[ -n "$EDIMA_USER" && "$EDIMA_USER" != "root" ]] || {
    printf 'Error: Could not determine the desktop user.\n' >&2
    exit 1
}

EDIMA_HOME="$(getent passwd "$EDIMA_USER" | cut -d: -f6)"

[[ -n "$EDIMA_HOME" && -d "$EDIMA_HOME" ]] || {
    printf 'Error: Could not determine home directory for %s.\n' "$EDIMA_USER" >&2
    exit 1
}


usage() {
    cat <<EOF
Edima OS installer

Usage:
  sudo ./install/setup.sh [profile] [--dry-run]

Profiles:
  minimal
  standard
  developer
  everything

Options:
  --dry-run    Preview installation without changing the system
  --help       Show this help

Examples:
  sudo ./install/setup.sh
  sudo ./install/setup.sh minimal
  sudo ./install/setup.sh developer
  sudo ./install/setup.sh everything
  sudo ./install/setup.sh everything --dry-run
EOF
}

error() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

while (($#)); do
    case "$1" in
        minimal|standard|developer|everything)
            PROFILE="$1"
            ;;
        --dry-run)
            DRY_RUN=1
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            error "Unknown argument: $1"
            ;;
    esac
    shift
done

[[ -f /etc/os-release ]] || error "/etc/os-release not found"

# shellcheck disable=SC1091
source /etc/os-release

[[ "${ID:-}" == "debian" ]] || \
    error "Edima OS currently targets Debian. Detected: ${ID:-unknown}"

ARCH="$(dpkg --print-architecture)"

case "$ARCH" in
    amd64|arm64)
        ;;
    *)
        error "Unsupported architecture: $ARCH"
        ;;
esac

source "$INSTALL_DIR/phases/system.sh"
source "$INSTALL_DIR/sources/docker.sh"
source "$INSTALL_DIR/phases/user.sh"

PROFILE_FILE="$PROFILE_DIR/$PROFILE.conf"
[[ -f "$PROFILE_FILE" ]] || error "Profile not found: $PROFILE"

# shellcheck disable=SC1090
source "$PROFILE_FILE"

[[ -n "${MANIFESTS:-}" ]] || \
    error "Profile contains no manifests: $PROFILE"

packages=()

for manifest in $MANIFESTS; do
    file="$MANIFEST_DIR/$manifest.txt"

    [[ -f "$file" ]] || \
        error "Manifest not found: $manifest"

    while IFS= read -r package || [[ -n "$package" ]]; do
        [[ -z "$package" ]] && continue
        [[ "$package" == \#* ]] && continue
        packages+=("$package")
    done < "$file"
done

((${#packages[@]})) || \
    error "No packages found for profile: $PROFILE"

mapfile -t packages < <(
    printf '%s\n' "${packages[@]}" | sort -u
)

printf 'Edima OS installer\n'
printf '%s\n' '=================='
printf 'Profile:      %s\n' "$PROFILE"
printf 'Architecture: %s\n' "$ARCH"
printf 'Manifests:    %s\n' "$MANIFESTS"
printf 'Packages:     %d\n' "${#packages[@]}"
printf '\n'

printf '%s\n' 'Packages:'
printf '  %s\n' "${packages[@]}"

if ((DRY_RUN)); then
    printf '\n%s\n' 'Calculating installation impact...'

    simulation="$(mktemp)"
    trap 'rm -f "$simulation"' EXIT

    if ! apt-get -s \
        --no-install-recommends \
        install "${packages[@]}" >"$simulation" 2>&1; then
        cat "$simulation" >&2
        error "APT could not resolve this installation."
    fi

    summary="$(
        grep -E '^[0-9]+ upgraded, [0-9]+ newly installed,' "$simulation" |
        head -n 1
    )"

    upgraded_packages="$(
        printf '%s\n' "$summary" |
        sed -nE 's/^([0-9]+) upgraded,.*/\1/p'
    )"

    new_packages="$(
        printf '%s\n' "$summary" |
        sed -nE 's/^[0-9]+ upgraded, ([0-9]+) newly installed,.*/\1/p'
    )"

    download_size="$(
        sed -nE 's/^Need to get ([^ ]+).*/\1/p' "$simulation" |
        head -n 1
    )"

    disk_size="$(
        sed -nE 's/^After this operation, ([^ ]+).*/\1/p' "$simulation" |
        head -n 1
    )"

    [[ -n "$download_size" ]] || download_size="0 B"
    [[ -n "$disk_size" ]] || disk_size="0 B"
    [[ -n "$upgraded_packages" ]] || upgraded_packages="0"
    [[ -n "$new_packages" ]] || new_packages="0"

    free_space="$(
        df -h --output=avail "$ROOT_DIR" |
        tail -n 1 |
        xargs
    )"

    printf '\n%s\n' 'Installation preview'
    printf '%s\n' '---------------------'
    printf 'Requested packages: %d\n' "${#packages[@]}"
    printf 'New packages:       %s\n' "$new_packages"
    printf 'Upgraded packages:  %s\n' "$upgraded_packages"
    printf 'Download:           %s\n' "$download_size"
    printf 'Additional disk:    %s\n' "$disk_size"
    printf 'Free disk:          %s\n' "$free_space"

    printf '\n%s\n' 'APT simulation:'
    grep -E '^(The following|[0-9]+ upgraded|Need to get|After this operation)' \
        "$simulation" || true

    printf '\nDry run: no changes made.\n'
    exit 0
fi

if ((EUID != 0)); then
    exec sudo "$0" "$@"
fi

if printf '%s\n' "$MANIFESTS" | grep -qw containers; then
    printf '\nConfiguring external package sources...\n'
    configure_docker_repository
fi

printf '\nInstalling system packages...\n'
install_system_packages packages

printf '\nConfiguring user tools for %s...\n' "$EDIMA_USER"
install_user_tools "$EDIMA_HOME"

printf '\nEdima OS installation complete.\n'
printf 'System packages: installed\n'
printf 'User tools:       configured for %s\n' "$EDIMA_USER"
