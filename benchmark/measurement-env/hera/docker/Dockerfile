# HERA replay image — one build per (corpus sha, condition).
#
# The build context is prepared by build.sh: `tree/` is a whitelist-filtered
# `git archive` export of one commit, already stripped for the condition. This
# file only copies and installs; it never selects or rewrites corpus content,
# so what the agent sees is decided entirely in build.sh and recorded in
# tree/.hera-image.json.
FROM python:3.12-slim

ARG CLAUDE_VERSION
ARG CODEX_VERSION

# Containers run as `--user <host uid>:<host gid>`, so nothing may resolve
# through the passwd database — HOME is fixed here and the shims read it.
ENV HOME=/home/hera \
    PATH=/home/hera/.local/bin:$PATH \
    JUPYTER_CONFIG_PATH=/home/hera/measurement_env/jupyter-config \
    JUPYTER_RUNTIME_DIR=/tmp/jupyter-runtime \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git libfaketime busybox-static \
        libglib2.0-0 libgl1 libegl1 libxkbcommon0 libfontconfig1 libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 1000 --create-home --shell /bin/bash hera

ENV QT_QPA_PLATFORM=offscreen

COPY --from=ghcr.io/astral-sh/uv:0.12.15 /uv /usr/local/bin/uv

RUN curl -fsSL https://claude.ai/install.sh | bash -s "$CLAUDE_VERSION"

# The Codex CLI and its code-mode host (the shell tool fails closed without it), static
# musl binaries from the release; `runner: codex` cases exec the former.
RUN for b in codex codex-code-mode-host; do \
        curl -fsSL "https://github.com/openai/codex/releases/download/rust-v${CODEX_VERSION}/${b}-x86_64-unknown-linux-musl.tar.gz" \
        | tar -xz -C /usr/local/bin \
        && mv "/usr/local/bin/${b}-x86_64-unknown-linux-musl" "/usr/local/bin/${b}" \
        && chmod 755 "/usr/local/bin/${b}"; \
    done \
    && codex --version

COPY tree /home/hera/measurement_env

# The cache goes with the sync: it is build-time debris, and its root-owned
# subdirs would be unwritable to the uid the container actually runs as.
RUN uv sync --frozen --project /home/hera/measurement_env \
    && rm -rf /tmp/uv-cache

# Mirrors scripts/install.sh's host install, except the agent prompt is copied
# rather than symlinked: the harness bind-mounts over paths under
# measurement_env, and a symlink would follow the mount.
RUN install -D -m 0644 /home/hera/measurement_env/hera/hera_tactical.md \
        /home/hera/.claude/agents/hera-tactical.md \
    && for shim in nb nb-collab menv; do \
        ln -s "/home/hera/measurement_env/tools/$shim" "/home/hera/.local/bin/$shim"; \
    done \
    && rm -f /home/hera/.claude/settings.json /home/hera/.claude/CLAUDE.md \
    && install -d /home/hera/.codex

COPY entrypoint.sh /usr/local/bin/hera-entrypoint

# The episode's clock. libfaketime hangs the claude binary and a past clock
# breaks its TLS, so the fake is split: every shell (tool calls, the
# entrypoint and its JupyterLab) goes through the bash wrapper, which applies
# libfaketime from HERA_FAKETIME; the claude process gets fakedate.js through
# BUN_OPTIONS, which shifts only what the model is told the date is. The
# codex binary is static, so it gets neither: its model reads the real date
# once, its shells the wrapper's clock. The Codex runner's exec-time render,
# harness notes and stop hook sit beside fakedate.js.
RUN mv /bin/bash /bin/bash.real
COPY bash-wrapper /bin/bash
COPY fakedate.js codex-config.py codex-notes.md codex-hook.py /opt/hera/
RUN chmod 755 /bin/bash && chmod 644 /opt/hera/*

RUN chmod -R a+rwX /home/hera \
    && install -d -m 1777 /tmp/jupyter-runtime /tmp/uv-cache /work

USER hera
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/hera-entrypoint"]

# Last, so a build stamp never costs a rebuild of the layers above. The same
# facts sit in tree/.hera-image.json for a reader inside the container.
ARG HARNESS_SHA
ARG CORPUS_SHA
ARG CONDITION
ARG PROMPT_SOURCE
LABEL science.sharpelab.hera.harness_sha="$HARNESS_SHA" \
      science.sharpelab.hera.corpus_sha="$CORPUS_SHA" \
      science.sharpelab.hera.condition="$CONDITION" \
      science.sharpelab.hera.prompt_source="$PROMPT_SOURCE" \
      science.sharpelab.hera.claude_version="$CLAUDE_VERSION" \
      science.sharpelab.hera.codex_version="$CODEX_VERSION"
