"""Render the episode's `$CODEX_HOME` right before `codex exec` starts (see
`hera.replay.codex.exec_args`): the agent prompt as `developer_instructions`, the run
config, the stop hook, and the credential when it comes as a file.

Runs inside the container with the image's python. The prompt is the image's
`hera/hera_tactical.md`, so a corpus-prompt overlay is honoured; its Claude agent
frontmatter is dropped and the harness notes (`codex-notes.md`) go in front of it. One
JSON line on stdout (`type: hera.codex_config`) records what was rendered; the run loop
keeps it beside the stream events.
"""

import base64
import hashlib
import json
import os
import re
import sys

PROMPT = "/home/hera/measurement_env/hera/hera_tactical.md"
NOTES = "/opt/hera/codex-notes.md"
HOOK = "/opt/hera/codex-hook.py"
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

# Top-level keys first (TOML), then the tables. `inherit = "all"`: the stubs read
# HERA_EPISODE_DIR and the bash wrapper reads HERA_FAKETIME, which the default `core`
# set drops. The feature flags remove the skills, plugin and app scaffolding Codex
# injects on its own; `multi_agent = false` leaves its team preamble in place and
# appends a retraction (what the harness gives). `web_search` is the top-level key;
# `features.web_search` is deprecated.
CONFIG = '''web_search = "disabled"
approval_policy = "never"
sandbox_mode = "danger-full-access"
project_doc_fallback_filenames = []
[history]
persistence = "save-all"
[shell_environment_policy]
inherit = "all"
[features]
multi_agent = false
plugins = false
apps = false
recommended_plugins = false
memories = false
skill_search = false
'''


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    home = os.environ["CODEX_HOME"]
    os.makedirs(home, exist_ok=True)
    with open(PROMPT, encoding="utf-8") as fh:
        prompt = FRONTMATTER.sub("", fh.read(), count=1)
    with open(NOTES, encoding="utf-8") as fh:
        notes = fh.read()
    instructions = notes + "\n" + prompt
    if "'''" in instructions:
        raise SystemExit("codex-config: the prompt contains ''' and cannot be a TOML literal")
    config = "developer_instructions = '''\n" + instructions + "'''\n" + CONFIG
    with open(os.path.join(home, "config.toml"), "w", encoding="utf-8") as fh:
        fh.write(config)
    hooks = {"hooks": {"PreToolUse": [{"matcher": "^Bash$", "hooks": [
        {"type": "command", "command": f"python3 {HOOK}", "timeout": 10}]}]}}
    with open(os.path.join(home, "hooks.json"), "w", encoding="utf-8") as fh:
        json.dump(hooks, fh)
    auth = "none"
    if os.environ.get("CODEX_API_KEY"):
        auth = "api_key"
    elif os.environ.get("HERA_CODEX_AUTH_JSON"):
        path = os.path.join(home, "auth.json")
        with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "wb") as fh:
            fh.write(base64.b64decode(os.environ["HERA_CODEX_AUTH_JSON"]))
        auth = "file"
    print(json.dumps({"type": "hera.codex_config", "prompt": PROMPT, "prompt_sha256": sha(prompt),
                      "notes_sha256": sha(notes), "developer_instructions_sha256": sha(instructions),
                      "config_sha256": sha(config), "hook": HOOK, "auth": auth}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
