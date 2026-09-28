#!/usr/bin/env bash
set -euo pipefail

configure_docker_repository() {
    if [[ -f /etc/apt/sources.list.d/docker.sources ]] &&
       [[ -f /etc/apt/keyrings/docker.asc ]]; then
        return 0
    fi

    printf 'Configuring Docker official APT repository...\n'

    install -m 0755 -d /etc/apt/keyrings

    curl -fsSL \
        https://download.docker.com/linux/debian/gpg \
        -o /etc/apt/keyrings/docker.asc

    chmod a+r /etc/apt/keyrings/docker.asc

    . /etc/os-release

    cat > /etc/apt/sources.list.d/docker.sources <<SOURCE
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: ${VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
SOURCE
}
