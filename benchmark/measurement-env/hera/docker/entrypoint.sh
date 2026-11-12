#!/usr/bin/env bash
# Container entrypoint. With arguments, run them instead — one-shot work runs
# as `docker run --rm <image> <cmd>`.
#
# With none: bring up the collaborative JupyterLab that the agent's nb-collab
# talks to, rooted at HERA_JL_ROOT on HERA_JL_PORT, and wait on it. Argv
# mirrors the rig launcher: --collaborative for the YDoc room,
# disable_check_xsrf because nb-collab's session preflight carries no token.
# The token is emptied on top of that: /api/status is @web.authenticated in
# jupyter_server 2.20, so the readiness gate — and any probe the harness runs
# through `docker exec` — would otherwise get a 403. The server binds loopback
# inside the container, so its only reachable callers are the agent and the
# harness. This script runs through the bash wrapper, so JupyterLab inherits
# the episode's clock when HERA_FAKETIME is set.
set -euo pipefail

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

PORT="${HERA_JL_PORT:-8888}"
ROOT="${HERA_JL_ROOT:-/work}"
mkdir -p "$JUPYTER_RUNTIME_DIR"

/home/hera/measurement_env/.venv/bin/python -m jupyterlab \
    --notebook-dir "$ROOT" --port "$PORT" --ServerApp.port_retries=0 \
    --ServerApp.ip=127.0.0.1 --no-browser --collaborative \
    --ServerApp.disable_check_xsrf=True --IdentityProvider.token= &
jl_pid=$!

# `docker stop` reaches PID 1 only; JupyterLab gets the same signal so it
# flushes the notebooks it holds instead of being killed with the container.
trap 'kill -TERM "$jl_pid" 2>/dev/null; wait "$jl_pid"; exit 0' TERM INT

for _ in $(seq 60); do
    if curl -fsS "http://127.0.0.1:$PORT/api/status" >/dev/null 2>&1; then
        echo "jupyterlab ready on 127.0.0.1:$PORT (pid $jl_pid), root=$ROOT"
        wait "$jl_pid"
        exit $?
    fi
    kill -0 "$jl_pid" 2>/dev/null || { echo "jupyterlab exited during startup" >&2; wait "$jl_pid"; exit 1; }
    sleep 1
done

echo "jupyterlab did not answer /api/status within 60s" >&2
exit 1
