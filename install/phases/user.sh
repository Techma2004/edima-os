#!/usr/bin/env bash
set -euo pipefail

install_user_tools() {
    local user_home="$1"
    local uv_bin="$user_home/.local/bin/uv"

    if [[ ! -x "$uv_bin" ]]; then
        printf 'Installing uv for %s...\n' "$EDIMA_USER"

        su - "$EDIMA_USER" -c \
            'curl -LsSf https://astral.sh/uv/install.sh | sh'
    fi

    [[ -x "$uv_bin" ]] || {
        printf 'Warning: uv installation did not produce %s\n' "$uv_bin" >&2
        return 1
    }

    if ! su - "$EDIMA_USER" -c "$uv_bin tool list 2>/dev/null | grep -q '^ruff '"; then
        su - "$EDIMA_USER" -c "$uv_bin tool install ruff"
    fi

    if ! su - "$EDIMA_USER" -c "$uv_bin tool list 2>/dev/null | grep -q '^pyright '"; then
        su - "$EDIMA_USER" -c "$uv_bin tool install pyright"
    fi
}
