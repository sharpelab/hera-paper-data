"""PreToolUse hook: the episode ends when the agent hands a measure cell to the
rig, or settles in to wait for it.

Installed by `hera-replay cut` as <session>/.claude/episode_stop.py. The
handoff itself is the nb-collab stub's business (it lands the append, never
executes, and writes <session>/episode-stop.json); the hera-watch stub writes
the same marker. This hook denies any ScheduleWakeup / Monitor call (in the
live sessions those only ever follow a handoff) and records it as the marker.
Once the marker exists, every later Bash / ScheduleWakeup / Monitor call (the
matcher's tools) is denied and ends the turn (`continue: false`), so
`claude -p` exits on its own with its result event. One exception: after the
watch arms (on the first code cell appended, which may be a prep cell), the
one Bash call that appends to the measure notebook goes through, so the cell
the watch was armed for lands.
"""

import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone

HEREDOC_BODY = re.compile(r"<<\s*-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\2[ \t]*(?=\n|$)", re.DOTALL)
MEASURE_SUFFIX = "_measure.ipynb"
WAIT_TOOLS = ("ScheduleWakeup", "Monitor")


def appends_to_measure(command):
    """Whether a Bash command has an `nb-collab append` naming a measure notebook."""
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


def stop_output(reason: str) -> dict:
    return {
        "continue": False,
        "stopReason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }


def main() -> int:
    payload = json.load(sys.stdin)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    marker = os.path.join(root, "episode-stop.json")
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if os.path.exists(marker):
        with open(marker, encoding="utf-8") as fh:
            record = json.load(fh)
        if (tool == "Bash" and record.get("tool") == "hera-watch" and "append_pass" not in record
                and "append_landed" not in record and appends_to_measure(tool_input.get("command", ""))):
            record["append_pass"] = payload.get("tool_use_id")
            with open(marker, "w", encoding="utf-8") as fh:
                json.dump(record, fh, indent=2)
            return 0
        json.dump(stop_output("episode complete"), sys.stdout)
        return 0
    if tool not in WAIT_TOOLS:
        return 0
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "command": json.dumps(tool_input),
        "invocation": tool,
        "cell_ids": [],
        "tool_use_id": payload.get("tool_use_id"),
    }
    with open(marker, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)
    json.dump(stop_output("episode complete"), sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
