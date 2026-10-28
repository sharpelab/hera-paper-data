#!/usr/bin/env python3
"""hera-notify — Slack notifications for live measurement sessions.

Thin wrapper over measurebot's Slack plumbing (bot token + user/channel
maps from ``~/.config/measurebot/.env``; see measurebot README). Lets the
session agent ping the operator — proposal landed, checkpoint verdict,
run complete, anomaly — instead of relying on them watching the terminal.

Explicit targets only: there is deliberately no default recipient — a
notification tool on a shared lab rig must never guess who to ping.
"""
from __future__ import annotations

import argparse
import sys

from measurebot.alerts import send_slack_channel_message, send_slack_dm


def main(argv: list[str] | None = None) -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(
        prog="hera-notify",
        description="Send a Slack notification to the session operator. "
        "Targets are measurebot config keys (SLACK_USER_<NAME> / "
        "SLACK_CHANNEL_<NAME> in ~/.config/measurebot/.env).",
    )
    p.add_argument("message", help="the notification text")
    p.add_argument(
        "--user",
        action="append",
        help="Slack user key (e.g. ZACKG); repeatable. With --channel, "
        "mentions the user(s) in the channel message instead of DMing.",
    )
    p.add_argument("--channel", help="Slack channel key (e.g. ALERTS)")
    args = p.parse_args(argv)

    if not args.user and not args.channel:
        p.error("specify --user and/or --channel — no default recipient by design")

    if args.channel:
        ok = send_slack_channel_message(args.message, channel=args.channel, user=args.user)
    else:
        ok = send_slack_dm(args.message, user=args.user)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
