"""Codex PreToolUse hook: the episode ends when the agent hands a measure cell to the
rig, or settles in to wait for it.

The Codex twin of `src/hera/replay/episode_stop.py`, installed by `codex-config.py` as
`$CODEX_HOME/hooks.json` (matcher `^Bash$`). Codex hands every `exec_command` to it with
Claude's payload shape (`tool_name`, `tool_input.command`, `tool_use_id`, `cwd`). The
handoff itself is the nb-collab / hera-watch stub's business; once <cwd>/episode-stop.json
exists every later command is denied, except the one measure-notebook append after a
watch armed first. Only `hookSpecificOutput.permissionDecision` is emitted: Codex 0.155
rejects an output carrying `continue` or `stopReason` outright, and the deny with it. A
deny does not end the turn; the run loop's marker poll does.
"""

import json
import os
import re
import shlex
import sys

HEREDOC_BODY = re.compile(r"<<\s*-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\2[ \t]*(?=\n|$)", re.DOTALL)
MEASURE_SUFFIX = "_measure.ipynb"


def appends_to_measure(command):
    """Whether a shell command has an `nb-collab append` naming a measure notebook."""
    stripped = HEREDOC_BODY.sub("<<HEREDOC", command).replace("\\\n", " ")
    lexer = shlex.shlex(stripped, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return False
    for i, tok in enumerate(tokens[:-1]):
        if tok == "nb-collab" and tokens[i + 1] == "append":
            j = i + 2
            while j < len(tokens) and not set(tokens[j]) <= set(lexer.punctuation_chars):
                if tokens[j].endswith(MEASURE_SUFFIX):
                    return True
                j += 1
    return False


def deny(reason):
    json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                      "permissionDecisionReason": reason}}, sys.stdout)


def main():
    payload = json.load(sys.stdin)
    home = os.environ.get("CODEX_HOME")
    if home:
        with open(os.path.join(home, "hook-log.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
    root = payload.get("cwd") or os.getcwd()
    marker = os.path.join(root, "episode-stop.json")
    if not os.path.exists(marker):
        return 0
    with open(marker, encoding="utf-8") as fh:
        record = json.load(fh)
    command = (payload.get("tool_input") or {}).get("command", "")
    if (record.get("tool") == "hera-watch" and "append_pass" not in record and "append_landed" not in record
            and appends_to_measure(command)):
        record["append_pass"] = payload.get("tool_use_id")
        with open(marker, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2)
        return 0
    deny("episode complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
