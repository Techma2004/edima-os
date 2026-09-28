#!/usr/bin/env bash
set -euo pipefail

install_user_tools() {
    local user_home="$1"

    if ! command -v uv >/dev/null 2>&1; then
        su - "$EDIMA_USER" -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    fi

    local uv_bin="$user_home/.local/bin/uv"

    if [[ -x "$uv_bin" ]]; then
        su - "$EDIMA_USER" -c "$uv_bin tool install ruff"
        su - "$EDIMA_USER" -c "$uv_bin tool install pyright"
    fi
}
