## HERA — VERIFY (session-start gate)

The brief's `[VERIFY]` checklist as one read-only cell. **Gets only — no
setpoint writes, no ramps, no range changes**; if it fails, nothing has moved.
Items, each printed `PASS`/`FAIL` with the numbers behind it:

1. **magnet** — `field()` and `_status()['field']` both within 0.02 T of zero;
   output enabled and persistent switch on (`field()` raises otherwise).
2. **SAFETIES vs device card** — the seven committed validator ranges read back
   off the live parameters and compared numerically against the card's
   operating-limits table (TG, BG, Si smart + raw, field cap, both T setpoints),
   plus the session field cap against the driver's `max_field_T`.
3. **thermometry** — both worker logfiles live (`assert_thermometry_live`,
   age ≤ 15 s / period ≤ 12 s: the rig card's 5 s cadence with the ≥ 2–3 period
   margin), then T_sample in [1.0, 1.4] K and T_vaporizer tracking base. Note
   the card quotes base as 1.2–1.3 K and setup read **1.176 K** — slightly
   under, so the window is opened to 1.0 K rather than failing a colder-than-spec
   fridge. Flag if you disagree.
4. **heaters off** — both LS335 ranges 0. Setpoints are printed for the record
   but are inert while the ranges are 0.
5. **gates parked / DC205** — TG, BG, Si all at 0 V; DC205 on range code 2
   (±100 V) with output on; `ramp_rate` still 0.5 V/s (consent-gated — this is
   a read, confirming nothing has raised it).
6. **contacts** — the in-kernel `WIRING` dict compared against the device card's
   provided configuration literal (source T_0, drain B_3, sr1 = B_1−B_2, sr2/sr3
   n.c.), `meas_config` gain/bias/drive-channel fields checked, and no
   `ContactMux`/`QSwitch` bound (hardwired breakout this cooldown).
7. **drive + lock-in state** — `sr1` amplitude and frequency (13.777 Hz per the
   card) and the resulting `I_bias` across the 100 MΩ bias resistor; then every
   lock-in's sensitivity, τ and filter slope printed. The rig card notes τ and
   slope are operator-set and are *not* captured in run metadata, so this print
   is where they live on disk for the session — and τ sets the swept-point
   settling floor everything downstream is priced against (see the note below).

**Not gated here — He budget.** The AMI 1700 is not bound in this kernel and I
am deliberately not connecting it: it is a shared TCP instrument that the influx
logger may hold, and stealing its socket is not worth a number I would only
print. **Zack — confirm the He budget covers the session when you give the
grant**; your "go for autonomy" carries that confirmation.

**Pricing note, for after the grant.** `sr0` and `sr1` are at τ = 0.3 s with a
24 dB/oct filter slope. STYLE's settling floor (k ≈ 7–10 at 24 dB/oct) puts a
properly-settled point at ~2–3 s, roughly 10× the rig card's 0.2–0.25 s/pt
rule of thumb — which would price a first gate map in the 6+ hour range rather
than ~1. I am not asking for a front-panel change on a guess: the Gate C
liveness cut will measure the actual per-point cost and the noise at the present
settings, and I will bring a specific τ/slope recommendation with data behind it
before anything long is committed.

Last line of the cell is the machine-readable verdict — `VERIFY: ALL GREEN` or
`VERIFY: FAIL <item>`. Per the brief the grant keys on that printed line: on
green I record grant + verdict in `session_notes.md` and engage E1; on any FAIL
or a missing verdict line the grant is void and I stay in E0 and ping you.
