#!/usr/bin/env bash
# Install local context for measurement-env: symlink vendored tools/ into PATH
# and the HERA agent files into Claude Code's agent registry.
# Idempotent — safe to re-run after each `git pull`. Existing symlinks
# pointing elsewhere are not overwritten; those installs are skipped and
# the script exits non-zero at the end so the skip is visible.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
local_bin="${HOME}/.local/bin"
claude_agents="${HOME}/.claude/agents"

mkdir -p "$local_bin" "$claude_agents"

skipped=0

install_link() {
    local src="$1"
    local dest="$2"
    if [[ -L "$dest" ]]; then
        local current
        current="$(readlink "$dest")"
        if [[ "$current" == "$src" ]]; then
            printf '  ok:   %s -> %s\n' "$dest" "$src"
            return 0
        fi
        printf '  skip: %s exists (symlink target=%s); expected %s\n' \
            "$dest" "$current" "$src" >&2
        skipped=$((skipped + 1))
        return 0
    fi
    if [[ -e "$dest" ]]; then
        # Regular file — likely a previous install via Git Bash on Windows
        # where `ln -s` falls back to copy. Refresh the content.
        rm -f "$dest"
    fi
    ln -sf "$src" "$dest"
    printf '  %s -> %s\n' "$dest" "$src"
}

printf 'installing shims into %s\n' "$local_bin"
install_link "$repo_root/tools/newclaude"     "$local_bin/newclaude"
install_link "$repo_root/tools/hera-session"  "$local_bin/hera-session"
install_link "$repo_root/tools/hera-mksession" "$local_bin/hera-mksession"
install_link "$repo_root/tools/hera-mkkit"    "$local_bin/hera-mkkit"
install_link "$repo_root/tools/hera-archive"  "$local_bin/hera-archive"
install_link "$repo_root/tools/iris"          "$local_bin/iris"
install_link "$repo_root/tools/hera-tactical" "$local_bin/hera-tactical"
install_link "$repo_root/tools/nb"            "$local_bin/nb"
install_link "$repo_root/tools/nb-collab"     "$local_bin/nb-collab"
install_link "$repo_root/tools/hera-watch"    "$local_bin/hera-watch"
install_link "$repo_root/tools/hera-utilization" "$local_bin/hera-utilization"
install_link "$repo_root/tools/hera-metrics"  "$local_bin/hera-metrics"
install_link "$repo_root/tools/menv"          "$local_bin/menv"
install_link "$repo_root/tools/hera-notify"   "$local_bin/hera-notify"
install_link "$repo_root/tools/chiron"        "$local_bin/chiron"
install_link "$repo_root/tools/hera-transcript-hook" "$local_bin/hera-transcript-hook"

printf 'installing agents into %s\n' "$claude_agents"
install_link "$repo_root/hera/hera_tactical.md" "$claude_agents/hera-tactical.md"
install_link "$repo_root/tools/hera-session.md" "$claude_agents/hera-session.md"
install_link "$repo_root/hera/iris.md"          "$claude_agents/iris.md"
install_link "$repo_root/hera/chiron.md"        "$claude_agents/chiron.md"

# Retire agent names superseded by the 2026-06-12 hera-tactical rename.
# Two provenance checks: symlink into this repo (Linux), or a regular file
# whose frontmatter names one of our shipped agents (Git Bash, where ln -s
# falls back to copy — seen on dgg-vti 2026-06-12: copies survived retire).
for stale in hera.md hera-vti.md; do
    dest="$claude_agents/$stale"
    if [[ -L "$dest" ]] && [[ "$(readlink "$dest")" == "$repo_root"/* ]]; then
        rm -f "$dest"
        printf '  retired: %s\n' "$dest"
    elif [[ -f "$dest" ]] && head -3 "$dest" | grep -qE '^name: (hera|hera-vti)$'; then
        rm -f "$dest"
        printf '  retired: %s (copy)\n' "$dest"
    fi
done

# Register the transcript-backup hook (Stop + PreCompact) in the user-scope
# ~/.claude/settings.json. Idempotent: matched by the stable
# "hera-transcript-hook" marker in the command string. The hook itself gates on
# HERA_SESSION_DIR, so registering it globally only affects HERA/IRIS sessions.
printf 'registering transcript-backup hook in %s\n' "$HOME/.claude/settings.json"
hook_path="$local_bin/hera-transcript-hook"
if command -v cygpath >/dev/null 2>&1; then
    # Windows: Claude Code may run hook commands via PowerShell/cmd, which won't
    # honor the bash shebang — invoke Git Bash explicitly by absolute path.
    hook_cmd="\"$(cygpath -w "$(command -v bash)")\" \"$(cygpath -w "$hook_path")\""
else
    hook_cmd="bash $hook_path"
fi
HERA_HOOK_CMD="$hook_cmd" uv run --no-project python - "$HOME/.claude/settings.json" <<'PY'
import json
import os
import sys

path = sys.argv[1]
cmd = os.environ["HERA_HOOK_CMD"]

try:
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}
except Exception as e:
    print(f"  hook: cannot parse {path} ({e}); leaving it untouched", file=sys.stderr)
    sys.exit(0)

hooks = settings.setdefault("hooks", {})

def ensure(event):
    # PreCompact takes an optional matcher (auto|manual); omitting it fires for
    # both. Stop has no matcher. So a matcher-less group is correct for each.
    groups = hooks.setdefault(event, [])
    for group in groups:
        for h in group.get("hooks", []):
            if "hera-transcript-hook" in h.get("command", ""):
                return False  # already registered
    groups.append({"hooks": [{"type": "command", "command": cmd}]})
    return True

added = [e for e in ("Stop", "PreCompact") if ensure(e)]
if added:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"  hook: registered hera-transcript-hook for {', '.join(added)}")
else:
    print("  hook: hera-transcript-hook already registered")
PY

if (( skipped > 0 )); then
    printf 'done with %d skipped — clean up manually and re-run if intentional.\n' "$skipped" >&2
    exit 1
fi

printf 'done.\n'
