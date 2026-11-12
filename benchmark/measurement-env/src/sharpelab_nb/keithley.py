"""Keithley 2400 bring-up state verification — read-first, write-never.

Bring-up verifies the gate Keithleys against the expected state table instead
of writing it. Range/mode writes on a live output can glitch the device, while
inherited NVRAM state is equally untrustworthy (two identical 2400s were found
in different averaging states, halving readbacks) — so the setup cell trusts
neither: it reads, compares, and stops on any mismatch. Normalization is a
deliberate operator act with the source at 0 V, never a bring-up side effect.
"""

from __future__ import annotations

from typing import Any

# Expected resting state for a gate 2400; cells override per instrument.
GATE_2400_DEFAULTS: dict[str, Any] = {
    "mode": "VOLT",
    "rangev": 21.0,
    "rangei": 1e-6,
    "nplci": 1.0,
}


def _averaging_on(inst) -> bool:
    return bool(int(float(inst.ask(":SENS:AVER:STAT?"))))


def assert_keithley_state(
    inst,
    *,
    volt: float = 0.0,
    volt_tol: float = 1e-3,
    **expect: Any,
) -> None:
    """Verify a 2400's state; raise on any mismatch. Makes **no writes**.

    ``expect`` maps parameter names to expected values (defaults:
    ``GATE_2400_DEFAULTS``). Averaging (``:SENS:AVER``) is checked first —
    when enabled it corrupts the very readbacks the other checks trust
    (the volt-halving artifact). String values compare by prefix,
    case-insensitive; floats to 0.1 %.
    """
    expect = {**GATE_2400_DEFAULTS, **expect}
    problems: list[str] = []
    readings: list[str] = []

    try:
        if _averaging_on(inst):
            count = inst.ask(":SENS:AVER:COUN?").strip()
            problems.append(
                f"SENS:AVER enabled (count {count}) — corrupts readbacks; want off"
            )
    except Exception as e:  # a VISA hiccup here must not pass silently
        problems.append(f"SENS:AVER unreadable ({e})")

    for name, want in expect.items():
        got = inst.parameters[name]()
        readings.append(f"{name}={got}")
        if isinstance(want, str):
            ok = str(got).strip().strip('"').upper().startswith(want.upper())
        else:
            ok = abs(float(got) - float(want)) <= abs(float(want)) * 1e-3
        if not ok:
            problems.append(f"{name} = {got!r} (want {want!r})")

    v = float(inst.volt())
    readings.append(f"volt={v:+.4f}")
    if abs(v - volt) > volt_tol:
        problems.append(f"volt = {v:+.4f} V (want {volt:+.4f} ± {volt_tol:g})")

    if problems:
        raise RuntimeError(
            f"{inst.name}: state mismatch — no writes made.\n  "
            + "\n  ".join(problems)
            + f"\n  Resolve deliberately: ramp the source to 0 V (volt.step set), "
            f"then normalize_keithley_state({inst.name}, ...) or fix by hand, "
            "and re-run this cell."
        )
    print(f"{inst.name}: state verified, no writes — " + ", ".join(readings))


def normalize_keithley_state(inst, **expect: Any) -> None:
    """The deliberate write path: set the expected state, then re-verify.

    Refuses unless the source reads 0 V — range/mode writes never happen on a
    live output. Also disables ``:SENS:AVER`` (readback-halving artifact).
    """
    expect = {**GATE_2400_DEFAULTS, **expect}
    v = float(inst.volt())
    if abs(v) > 1e-3:
        raise RuntimeError(
            f"{inst.name}: source reads {v:+.4f} V — ramp to 0 V first "
            "(volt.step set), then normalize"
        )
    inst.write(":SENS:AVER:STAT 0")
    for name, want in expect.items():
        inst.parameters[name].set(want)
    assert_keithley_state(inst, **expect)
