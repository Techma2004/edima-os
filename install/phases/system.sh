#!/usr/bin/env bash
set -euo pipefail

install_system_packages() {
    local -n packages_ref=$1

    apt-get update
    apt-get install -y --no-install-recommends "${packages_ref[@]}"
}
