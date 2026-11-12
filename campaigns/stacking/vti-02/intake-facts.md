# Intake facts — vti-02

*Shield-provided values for the vti-02 kit (source: Aaron's handoff form,
2026-08-21, re-drafted by Zack onto the current form and signed off by
Aaron the same day over Signal). BIAS_R, DRIVE_FREQ, SR0_GAIN and the
per-lock-in gains per Aaron over Signal, 2026-08-21; T_CAP_K 100 per
Aaron ("for consistency"), superseding the form's 150. Lock-in naming
normalized to the VTI convention (`sr0…sr3`); Aaron labels the
GPIB0::18 unit `sr4`. Per-lock-in gains have no card slot and ride in
NOTES.*

---

ALIAS: vti-02
OWNER: Aaron
MATERIAL: 4LGr
SI_GATE: yes
T_TG_NM: 9.5
T_BG_NM: 11
TG_LIMIT: [−0.3, +1.0] V
BG_LIMIT: [−1.3, +2.0] V
SI_LIMIT: [−25, +25] V
B_CAP_T: 10.0
T_CAP_K: 100
TG_ADDR: GPIB0::1
BG_ADDR: GPIB0::24
SI_ADDR: ASRL7
BIAS_CHANNEL: sr1
LOCKIN_ADDRS: `sr0` GPIB0::22, `sr1` GPIB0::14, `sr2` GPIB0::19, `sr3` GPIB0::18
BIAS_R: 100 MOhm
DRIVE_FREQ: 13.777 Hz
SR0_GAIN: −1E6
SR1_GAIN: 1
SR2_GAIN: n.c.
SR3_GAIN: n.c.
CONTACT_LIVENESS: Alive: T_0, B_1, B_2, B_3. Dead: T_1, T_2, T_3, T_4.

## CONTACT_MAP

Bonded pads (label = position, T = top arc L→R, B = left side then
bottom L→R). Only the provided configuration below is wired to
instruments this cooldown:

| Label | Pad | | Label | Pad |
|---|---|---|---|---|
|  -  | -  | | T_0 | 29 |
| B_1 | 12 | | T_1 | 41 |
| B_2 | 04 | | T_2 | 01 |
| B_3 | 27 | | T_3 | 42 |
|  -  | -  | | T_4 | 43 |

## PROVIDED_CONFIG

| role | label |
|---|---|
| source        | T_0 |
| drain (`sr0`) | B_3 |
| `sr1` (Rxx)   | B_1 - B_2 |
| `sr2` (Rxx)   | n.c. |
| `sr3` (Rxx)   | n.c. |

## NOTES

Lock-in gains: `sr1` 1 (unity); `sr2`, `sr3` n.c.
