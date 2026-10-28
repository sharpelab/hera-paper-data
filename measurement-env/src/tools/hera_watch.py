#!/usr/bin/env python3
"""hera-watch — live run-dir digest for agent monitoring.

Watches an in-progress sweep run dir and emits a compact one-line-per-landed
-row digest to stdout (gain division applied, progress + ETA), so a Claude
Code background monitor can tail summaries instead of TSV rows. Runs against
a completed run dir too (digest-then-exit), doubling as a post-run summary.

    hera-watch data/3                 # watch run 3 until it completes
    hera-watch data/3 --once          # digest current state, exit
    hera-watch data/5 --channels sr1,sr2
    hera-watch data/5 --raw           # skip gain division (escape hatch)
    hera-watch data/7 --follow        # no deadline — backgrounded multi-hour run
    hera-watch data --next            # arm the NEXT run before the cell runs

Two independent budgets keep this both foreground-safe and long-run capable:

  * ``--timeout`` bounds the *measurement* watch. Default 570s — below the
    harness's ~600s foreground shell cap, so a foreground call can never
    outlive it. ``--follow`` lifts the deadline entirely; use it with a
    backgrounded invocation for multi-hour sweeps so it never self-exits and
    forces a re-arm.
  * ``--wait-start`` bounds the *human* wait for the run dir to appear (arm
    before the operator runs the cell). Default 1800s; on timeout the watch
    exits 2 so the agent can ping the operator.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from hera.watch import build_model, wait_for_next_run, wait_for_run, watch


def _flush_print(msg: str) -> None:
    """``print`` that flushes every line.

    ``--follow`` runs are backgrounded (stdout is a pipe, not a TTY), where the
    default is block buffering — a multi-hour sweep's per-row digests would sit
    in an 8 KB buffer and never reach a mid-run checkpoint read. Forcing a flush
    after each line makes every landed-row digest visible promptly. (QC0426
    2026-06-16: the agent saw only the pre-watch 'waiting…' line and read the
    run as stalled because the digest stream was buffered.)"""
    print(msg, flush=True)


def _install_sigpipe_handler() -> None:
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ImportError):
        pass


def main(argv: list[str] | None = None) -> int:
    _install_sigpipe_handler()
    if sys.platform == "win32":
        # Windows consoles default to cp1252; digest lines contain Ω/≈/→.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    p = argparse.ArgumentParser(
        prog="hera-watch",
        description="Live run-dir digest: one line per landed sweep row "
        "(gain-divided Rxx/I stats + progress/ETA) for an agent to tail.",
    )
    p.add_argument("run_dir",
                   help="sweep run directory (contains metadata.json + data.tsv). "
                   "May not exist yet — the watch waits up to --wait-start for it "
                   "to appear. With --next, give a data/ dir instead.")
    p.add_argument("--next", action="store_true",
                   help="treat run_dir as a data/ dir and latch onto the NEXT run "
                   "to appear (arm before the cell runs). Robust to 2nd+ runs and "
                   "lowest-free-id allocation — snapshots existing runs, waits for "
                   "a new one.")
    p.add_argument("--once", action="store_true",
                   help="digest current state then exit (no watch loop)")
    p.add_argument("--poll", type=float, default=5.0,
                   help="poll interval in seconds while watching (default 5)")
    p.add_argument("--timeout", type=float, default=570.0,
                   help="stop the measurement watch after this many seconds "
                   "(default 570, sub-CC-Bash-cap). See --follow.")
    p.add_argument("--follow", action="store_true",
                   help="watch to completion with no deadline (multi-hour runs); "
                   "overrides --timeout. Use with a backgrounded invocation.")
    p.add_argument("--wait-start", type=float, default=1800.0,
                   help="if run_dir doesn't exist yet, wait up to this many seconds "
                   "for it to appear (default 1800; <=0 waits indefinitely)")
    p.add_argument("--channels", default=None,
                   help="comma-separated lock-in channels to include (e.g. sr1,sr2). Default: all.")
    p.add_argument("--raw", action="store_true",
                   help="report raw lock-in X (skip gain division). Escape hatch.")
    p.add_argument("--bias-current", type=float, default=None,
                   help="override I_bias in amps (default: bias_voltage/bias_resistor from metadata)")
    p.add_argument("--every", type=int, default=25,
                   help="1D sweeps: emit a digest line every N new rows (default 25)")
    p.add_argument("--fs-warn", type=float, default=0.90,
                   help="warn when a lock-in's max|X| reaches this fraction of "
                   "its full-scale sensitivity (default 0.90; SR830 rails ~1.09×). "
                   "Requires sensitivity in the instrument snapshot.")
    p.add_argument("--leak-excess-warn", type=float, default=100e-12,
                   help="warn when a gate current's excess over its baseline "
                   "(max|I - I0|) reaches this many amps on 2+ consecutive "
                   "points (default 100e-12 = 100 pA)")
    args = p.parse_args(argv)

    timeout = None if args.follow else args.timeout

    if args.next:
        # Latch onto the NEXT run dir to appear under the data/ dir. Snapshots
        # the runs already present (the arm moment) and waits for a new one —
        # robust to 2nd+ runs, lowest-free-id allocation, and the arm-after-
        # start race that a frozen max+1 prediction got wrong.
        run_dir = wait_for_next_run(args.run_dir, timeout=args.wait_start,
                                    poll=args.poll, emit=_flush_print)
        if run_dir is None:
            print(f"error: no new run appeared under {args.run_dir} within "
                  f"{args.wait_start:.0f}s", file=sys.stderr)
            return 2
    else:
        # Arm before the run exists: poll for the specific dir to appear (a
        # plain target may also not exist yet when armed early).
        run_dir = Path(args.run_dir)
        if not wait_for_run(run_dir, timeout=args.wait_start, poll=args.poll,
                            emit=_flush_print):
            print(f"error: run dir {run_dir} did not appear within "
                  f"{args.wait_start:.0f}s", file=sys.stderr)
            return 2

    channels = [c.strip() for c in args.channels.split(",") if c.strip()] if args.channels else None
    try:
        model = build_model(run_dir, channels=channels,
                            bias_current=args.bias_current,
                            fs_warn=args.fs_warn,
                            leak_excess_warn=args.leak_excess_warn)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if not model.channels:
        sel = f" matching {args.channels!r}" if args.channels else ""
        print(f"warning: no lock-in (_X) channels{sel} in {run_dir}", file=sys.stderr)

    return watch(
        model, raw=args.raw, every=args.every, poll=args.poll,
        timeout=timeout, once=args.once, emit=_flush_print,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except Exception:
            pass
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
