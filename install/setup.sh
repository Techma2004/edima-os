#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="$ROOT_DIR/install"
MANIFEST_DIR="$INSTALL_DIR/manifests"
PROFILE_DIR="$INSTALL_DIR/profiles"

PROFILE="standard"
DRY_RUN=0

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
  --dry-run    Show what would be installed without changing the system
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

PROFILE_FILE="$PROFILE_DIR/$PROFILE.conf"
[[ -f "$PROFILE_FILE" ]] || error "Profile not found: $PROFILE"

# shellcheck disable=SC1090
source "$PROFILE_FILE"

[[ -n "${MANIFESTS:-}" ]] || error "Profile contains no manifests: $PROFILE"

packages=()

for manifest in $MANIFESTS; do
    file="$MANIFEST_DIR/$manifest.txt"

    [[ -f "$file" ]] || error "Manifest not found: $manifest"

    while IFS= read -r package || [[ -n "$package" ]]; do
        [[ -z "$package" ]] && continue
        [[ "$package" == \#* ]] && continue
        packages+=("$package")
    done < "$file"
done

((${#packages[@]})) || error "No packages found for profile: $PROFILE"

mapfile -t packages < <(printf '%s\n' "${packages[@]}" | sort -u)

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
    printf '\nDry run: no changes made.\n'
    exit 0
fi

if ((EUID != 0)); then
    error "Run the installer with sudo."
fi

printf '\nUpdating package metadata...\n'
apt-get update

printf '\nInstalling Edima packages...\n'
DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends "${packages[@]}"

printf '\nEdima OS package installation complete.\n'
