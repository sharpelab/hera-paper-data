#!/usr/bin/env bash
# Build the HERA replay image.
#
#   build.sh <harness_sha> [--corpus <sha>] [--corpus-prompt] [condition ...]
#
# Without --corpus, one image per (sha, condition), tagged
# hera-agent:<sha7>-<condition>: code, tools and corpus all from that commit.
# With --corpus, CORPUS_PATHS come from that commit instead — modern harness,
# older corpus — tagged hera-agent:<harness7>.c<corpus7>-<condition>, the
# corpus sha carrying a trailing `p` when --corpus-prompt moves the agent
# prompts with it. The condition's STRIP applies after the overlay.
#
# The context is a `git archive` export — only committed content ever reaches a
# build — filtered down to WHITELIST and then emptied of the condition's STRIP
# paths. Prints one JSON line per image; writes nothing outside the images
# themselves.
set -euo pipefail

CLAUDE_VERSION=2.1.283
CODEX_VERSION=0.157.1

# The agent-visible surface. Everything else in the commit is dropped, so a
# corpus file only reaches the agent by being added here. src/ is listed one
# level down: the six package dirs the wheel names, with src/hera reduced to
# the modules the agent's tools use (analysis, watch, the gate-map classifier)
# so that replay, grading and experiment harness code never ships.
WHITELIST=(
    CLAUDE.md
    README.md
    pyproject.toml
    uv.lock
    .python-version
    src/gui
    src/sharpelab_nb
    src/tools
    src/workers
    src/drivers
    src/hera/__init__.py
    src/hera/analysis.py
    src/hera/assets
    src/hera/cache.py
    src/hera/classify.py
    src/hera/models.py
    src/hera/overlay.py
    src/hera/prompt.py
    src/hera/provider.py
    src/hera/providers
    src/hera/render.py
    src/hera/sidecar.py
    src/hera/watch.py
    lib
    # uv.lock pins jupyterlab-cell-index to a wheel under vendor/; without it
    # `uv sync --frozen` cannot resolve.
    vendor
    docs/api
    jupyter-config
    tools/nb
    tools/nb-collab
    tools/menv
    hera/CLAUDE.md
    hera/recipes
    hera/crops
    hera/models
    hera/rig-cards
    hera/device-cards
    hera/templates
    hera/vti
    hera/blinding.md
    hera/session_template.md
    hera/hera_tactical.md
    hera/iris.md
    # Method documents the recipes cite by path (the live agent had the whole
    # repo). Never hera/docs wholesale: it holds the session archives.
    hera/docs/tetralayer-stacking-extraction-survey.md
    hera/docs/stacking-extraction-survey.md
    hera/docs/raman-public-data.md
    hera/docs/notebook-indexes
    hera/docs/iris
    hera/docs/papers
)

# Condition -> paths emptied for it. Stripped directories stay in place as
# empty dirs so corpus paths still resolve.
declare -A STRIP=(
    [full]=""
    [none]="hera/recipes hera/crops"
)

# The corpus axis: what --corpus replaces wholesale. The method knowledge the
# agent reads — recipes, the worked examples cropped for them, and the forward
# models the investigations lean on, which only make sense at their recipes'
# vintage. Everything else, code and cards alike, stays at the harness sha.
CORPUS_PATHS=(
    hera/recipes
    hera/crops
    hera/models
    hera/docs/tetralayer-stacking-extraction-survey.md
    hera/docs/stacking-extraction-survey.md
    hera/docs/raman-public-data.md
    hera/docs/notebook-indexes
    hera/docs/iris
    hera/docs/papers
)

# Prompts are protocol, not method, so they follow the harness; --corpus-prompt
# moves them to the corpus sha for the experiment that asks whether a prompt of
# that vintage reproduces a failure of that vintage.
PROMPT_PATHS=(
    hera/hera_tactical.md
    hera/iris.md
)

die() { printf 'build.sh: %s\n' "$*" >&2; exit 1; }

usage="usage: build.sh <harness_sha> [--corpus <sha>] [--corpus-prompt] [condition ...]"
[ "$#" -ge 1 ] || die "$usage"
harness_arg="$1"; shift
corpus_arg=""
corpus_prompt=0
conditions=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        --corpus) [ "$#" -ge 2 ] || die "--corpus needs a sha"; corpus_arg="$2"; shift 2 ;;
        --corpus-prompt) corpus_prompt=1; shift ;;
        -*) die "unknown option: $1"$'\n'"$usage" ;;
        *) conditions+=("$1"); shift ;;
    esac
done
[ -n "$corpus_arg" ] || [ "$corpus_prompt" -eq 0 ] || die "--corpus-prompt needs --corpus"
[ "${#conditions[@]}" -gt 0 ] || conditions=(full none)

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
docker_dir="$repo/hera/docker"

harness="$(git -C "$repo" rev-parse --verify "${harness_arg}^{commit}")" \
    || die "no such commit: $harness_arg"
harness7="${harness:0:7}"
corpus="$harness"
overlay=()
prompt_source="harness"
tag_sha="$harness7"
if [ -n "$corpus_arg" ]; then
    corpus="$(git -C "$repo" rev-parse --verify "${corpus_arg}^{commit}")" \
        || die "no such commit: $corpus_arg"
    overlay=("${CORPUS_PATHS[@]}")
    tag_sha="${harness7}.c${corpus:0:7}"
    if [ "$corpus_prompt" -eq 1 ]; then
        overlay+=("${PROMPT_PATHS[@]}")
        prompt_source="corpus"
        tag_sha="${tag_sha}p"
    fi
fi
built_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# These come from the working tree, not the archived sha, so the image records
# what assembled it.
docker_files=(Dockerfile entrypoint.sh bash-wrapper fakedate.js codex-config.py codex-notes.md codex-hook.py)
docker_dir_sha="$(cd "$docker_dir" && cat "${docker_files[@]}" | sha256sum | cut -c1-64)"

for condition in "${conditions[@]}"; do
    [ -n "${STRIP[$condition]+set}" ] || die "unknown condition: $condition"
done

json_array() {
    # Positional args -> a JSON array on one line.
    local out="" item
    for item in "$@"; do
        out+="${out:+, }\"$item\""
    done
    printf '[%s]' "$out"
}

for condition in "${conditions[@]}"; do
    ctx="$(mktemp -d)"
    trap 'rm -rf "$ctx"' EXIT
    export_dir="$ctx/export"
    tree="$ctx/tree"
    mkdir -p "$export_dir" "$tree"

    git -C "$repo" archive --format=tar "$harness" | tar -x -C "$export_dir"

    # Wholesale replacement, not a merge: the harness copy goes first, so a file
    # the corpus sha never had cannot survive into the image, and an overlay path
    # missing at the corpus sha stays missing.
    present=()
    for path in "${overlay[@]}"; do
        rm -rf "${export_dir:?}/$path"
        if git -C "$repo" cat-file -e "$corpus:$path" 2>/dev/null; then present+=("$path"); fi
    done
    [ "${#present[@]}" -eq 0 ] \
        || git -C "$repo" archive --format=tar "$corpus" -- "${present[@]}" | tar -x -C "$export_dir"

    for path in "${WHITELIST[@]}"; do
        [ -e "$export_dir/$path" ] || continue
        mkdir -p "$tree/$(dirname "$path")"
        cp -a "$export_dir/$path" "$tree/$path"
    done

    # Every `hera.<module>` the kept code imports must itself be kept. A hit means
    # the whitelist and the shipped code have drifted apart — report it rather
    # than quietly widening the surface.
    hits="$(cd "$tree" && grep -rnoE \
        '^\s*(from\s+hera\.([A-Za-z_]+)|import\s+hera\.([A-Za-z_]+)|from\s+hera\s+import\s+([A-Za-z_]+))' \
        --include='*.py' src tools 2>/dev/null \
        | while IFS=: read -r file line match; do
            mod="$(printf '%s' "$match" | sed -E 's/.*hera[. ]+(import )?//; s/[^A-Za-z_].*//')"
            [ -e "src/hera/$mod.py" ] || [ -d "src/hera/$mod" ] || printf '%s:%s: hera.%s\n' "$file" "$line" "$mod"
        done)"
    [ -z "$hits" ] || die "kept code imports a module the whitelist drops:"$'\n'"$hits"

    strip=(${STRIP[$condition]})
    for path in "${strip[@]}"; do
        rm -rf "${tree:?}/$path"
        mkdir -p "$tree/$path"
    done

    CORPUS_SHA="$corpus" HARNESS_SHA="$harness" PROMPT_SOURCE="$prompt_source" \
    OVERLAY_JSON="$(json_array "${overlay[@]}")" \
    CONDITION="$condition" BUILT_AT="$built_at" \
    CLAUDE_VERSION="$CLAUDE_VERSION" CODEX_VERSION="$CODEX_VERSION" DOCKER_DIR_SHA256="$docker_dir_sha" \
    WHITELIST_JSON="$(json_array "${WHITELIST[@]}")" \
    STRIP_JSON="$(json_array "${strip[@]}")" \
    uv run --no-project python - "$tree/.hera-image.json" <<'PY'
import json
import os
import sys

overlay = json.loads(os.environ["OVERLAY_JSON"])
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(
        {
            "corpus_sha": os.environ["CORPUS_SHA"],
            "condition": os.environ["CONDITION"],
            # Only an overlay build separates the two; a plain image carries the
            # single sha its whole tree came from.
            **({"harness_sha": os.environ["HARNESS_SHA"],
                "prompt_source": os.environ["PROMPT_SOURCE"],
                "corpus_paths": overlay} if overlay else {}),
            "whitelist": json.loads(os.environ["WHITELIST_JSON"]),
            "strip": json.loads(os.environ["STRIP_JSON"]),
            "claude_version": os.environ["CLAUDE_VERSION"],
            "codex_version": os.environ["CODEX_VERSION"],
            "docker_dir_sha256": os.environ["DOCKER_DIR_SHA256"],
            "built_at": os.environ["BUILT_AT"],
        },
        f,
        indent=2,
    )
    f.write("\n")
PY

    # The Dockerfile, entrypoint, clock shims and the Codex runner's files come
    # from the working tree, not the archive: how the image is assembled is not
    # part of the frozen corpus.
    for f in "${docker_files[@]}"; do cp "$docker_dir/$f" "$ctx/"; done

    tag="hera-agent:${tag_sha}-${condition}"
    docker build --build-arg "CLAUDE_VERSION=$CLAUDE_VERSION" --build-arg "CODEX_VERSION=$CODEX_VERSION" \
        --build-arg "HARNESS_SHA=$harness" --build-arg "CORPUS_SHA=$corpus" \
        --build-arg "CONDITION=$condition" --build-arg "PROMPT_SOURCE=$prompt_source" \
        -t "$tag" "$ctx" >&2
    id="$(docker image inspect --format '{{.Id}}' "$tag")"
    printf '{"tag": "%s", "id": "%s", "sha": "%s", "corpus_sha": "%s", "prompt_source": "%s", "condition": "%s"}\n' \
        "$tag" "$id" "$harness" "$corpus" "$prompt_source" "$condition"

    rm -rf "$ctx"
    trap - EXIT
done
