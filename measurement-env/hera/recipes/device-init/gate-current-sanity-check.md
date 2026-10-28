# Gate current sanity check

## What
A sanity check at the start of a cooldown: sweep each active gate from 0 out
to each of its previously established card limits (others parked at 0),
watching gate current at pA resolution — does it leak, or does it look safe?
Safe → move on. Leaks → stop and report. Not a leakage test; a quick
liveness-and-gross-safety pass before the campaign starts.

## When
Once per cooldown, after instrument init and the measurement-config block,
before any subsequent recipe. Optionally also after thermal cycling or
physical intervention (reseating contacts, swapping a bias source).

**Preconditions:**
- Card-provided gate limits exist (device card, or a prior `gate-range-finding`).
- Gates ungrounded, device in a measurable configuration.

## Why
This is the cooldown's liveness check, run before any measurement because
everything downstream assumes it holds: the device is alive — passes a
measurable current — and every gate stays clean across the range the campaign
will use. The gate validators are already committed (the gate-validators slot,
from the card); this check confirms the device is actually safe within them. A
gate that leaks within its range is a data and device-safety problem. This is
a liveness and gross-safety check, not a leakage test: characterizing a
leakage onset is `gate-leakage-survey`, re-deriving the range is
`gate-range-finding`.

## Recipe

Two cells. HERA proposes both together. The human runs Cell A once — it loops
every leg (each gate × both polarities), each leg getting its own file and
slug — watching the live gate-current plot, then runs Cell B once. No
copy-the-cell iteration: the legs are enumerated up front.

### Cell A — gate sweep

Sweeps every active gate from 0 to each of its card limits, other gates
parked at 0. `nplci=10` on the gate-current channels for high-SNR pA
readback (~167 ms/pt); it stays at 10 across the sweep, Cell B resets it.

```python
# === Gate sweep: every active gate, 0 -> each of its card limits ===
# Endpoints = the device-card gate limits set as TG_MIN/TG_MAX, BG_MIN/BG_MAX in the
# gate-validators slot. Nothing to hand-substitute.
# Watch the live gate-current plot per leg: pA, riding the charging slope = safe.
# A gross turn-up off that slope = it's leaking -> Kernel Interrupt (the try/finally
# parks the gate); stop and report (skip Cell B).

# one leg per gate per polarity, (gate, endpoint)
legs = [
    (k_tg, TG_MAX), (k_tg, TG_MIN),
    (k_bg, BG_MAX), (k_bg, BG_MIN),
]
n_pts   = 251
delay   = 1            # s
lockins = [sr830_1, sr830_2, sr830_3, sr830_4]   # match your mc

# pA-floor readback on the gate-current channels; Cell B resets to 1.
k_tg.nplci(10)
k_bg.nplci(10)

# AC sense drive ~1 nA (liveness current) via the device-card drive->current relation
# — don't inherit the lock-in's residual amplitude (it starves the X read).
sr830_1.amplitude(<amp for ~1 nA per device card>)

for gate, v_endpoint in legs:
    s = sweep.AsyncStation(measurement_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {gate.name}')
    s.add_comment(f'leg: 0 -> {v_endpoint:+g} V (card limit)')

    # park gates at 0 (the swept one starts from 0)
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)

    xp = gate.volt
    other = k_bg if gate is k_tg else k_tg
    # temperature: fp it per the rig card's polling rules
    # The swept gate's V is already the sweep's setpoint column — re-fp'ing it
    # writes a duplicate column name. fp the held gate's V + both currents.
    s.fp(other.volt)
    s.fp(gate.curr).fp(other.curr)
    s.plot(xp, k_tg.curr)
    s.plot(xp, k_bg.curr)
    for lia in lockins:
        s.fp(lia.X).fp(lia.P)
        s.plot(xp, lia.X)

    try:
        s.sweep(gate.volt, np.linspace(0, v_endpoint, n_pts), delay=delay)
    finally:
        s.ramp(gate.volt, 0)
```

Each leg's endpoint is a device-card gate limit — the `TG_MIN/TG_MAX`,
`BG_MIN/BG_MAX` set in the gate-validators slot — so there are no limit numbers
to hand-substitute; HERA just lists the legs. The `lockins` list should match
the channels in your `measurement_config`; if `mc` lists exactly the active
sr830s HERA may pre-fill it, otherwise the human sets it.

Read the live plot per leg:
- Lock-in `X`: nonzero, smoothly varying → device alive.
- Swept gate `*.curr`: stays in pA, on the capacitive charging slope, to the
  limit → safe.
- Parked gate `*.curr`: at the readback floor → no cross-gate path.

A geometry-derived ceiling (≈ ±0.5 V/nm × hBN thickness for the metal gates)
sanity-checks the card limits themselves: if a card limit exceeds it, treat
the card as suspect — don't sweep to it, flag to the operator before running.

### Cell B — reset nplci

After every leg has run, reset gate-current `nplci` back to standard. Only run
this if every leg looked safe; if anything leaked, stop and report instead (a
leaking gate is `gate-leakage-survey`'s problem, not this recipe's).

```python
# === Reset gate-current nplci ===
# Validators were already committed in the gate-validators slot — nothing to re-commit.
# Undo Cell A's nplci bump; print the live validators to confirm.
k_tg.nplci(1)
k_bg.nplci(1)

print("k_tg.volt validator:", k_tg.volt.vals)
print("k_bg.volt validator:", k_bg.volt.vals)
```

### HERA handshake

HERA proposes Cell A (all legs) and Cell B together, and **does not propose
any subsequent recipe step until the human reports the per-leg results.** If
everything looked safe HERA moves on; if any gate leaked HERA stops and
reports — it never advances on a gate that leaked. Human is the gate; HERA
waits.

### Failure-mode catalog

| What you see on the live plot | What it means | Action |
|---|---|---|
| Lock-in `X` nonzero and smoothly varying | Device alive, contact wiring good | Continue |
| Lock-in `X` flat zero on one channel | Wiring break on that contact pair | Stop; check wiring |
| Lock-in `X` flat-nonzero, **all channels at the same value** | Device tied to ground (shared-node short) — false signal that mimics readback | Stop; unground the device, then re-run Cell A |
| `k_*.curr` saturated at full-range readback (e.g. ±1 µA on `rangei=1e-6`) | Range too coarse for the leakage scale, or a real leak that pinned the range | Drop `rangei` to `1e-9` and re-run; if still saturated, real leak |
| `k_*.curr` makes a gross turn-up off the capacitive charging slope | It's leaking | Interrupt; stop and report (don't run Cell B); `gate-leakage-survey` to characterize |
| Parked gate `*.curr` tracks the swept gate | Cross-gate leakage path | Stop; characterize via `gate-leakage-survey` |

## Examples

- `aaron/RPL_10/241207_measure.ipynb` cells 22–25 — an early one-shot
  liveness check: three small fixed `0 → +1 V` sweeps (TG, BG, Si BG),
  full-range sweeps deferred to separate per-gate recipes. The canonical
  liveness shape; the loop here generalizes it to the card limits.
- `isaac/b1c2_toploader/20260505_measure.ipynb` cells 17–27 — first live
  HERA test, an early version of this recipe in action. Cell 22 is the sweep cell with
  `nplci=10` (using the older save/restore pattern). Hit the grounded-device
  failure mode (cell 26 diagnoses: sr830_2/3/4 share contact 30, all locked
  to ground potential). After ungrounding, manual range-finding established
  `k_tg.volt = (-7, +6)` and `k_bg.volt = (-4, +4.4)`; cell 27 commits the
  validators. The session also surfaced that `KEITHLEY_DEFAULTS["rangei"]`
  should be `1e-9` for pA-resolution; the b1c2 template was patched
  in-session.

## Next

- **Safe**: move on to the campaign's next recipe — every gate swept clean to
  its card limit on each side, and the `add_comment` slug captured the recipe
  identity in metadata.
- **Leaks**: stop and report; the operator decides whether to characterize via
  `gate-leakage-survey` or re-derive limits via `gate-range-finding`.
- **Results not reported**: HERA will not advance.
