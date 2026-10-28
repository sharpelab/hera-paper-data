# Intake facts — vti-01

*Shield-provided values for the vti-01 kit (source: Aaron's amended
handoff form, 2026-08-18; BIAS_R per the owner's handoff message —
provenance in `../deviations.md`; DRIVE_FREQ queried from the bias
lock-in at intake; SR0_GAIN per Aaron 2026-08-19). Lock-in naming
normalized to the VTI convention (`sr0…sr3`).*

---

ALIAS: vti-01
OWNER: Jordan
MATERIAL: 3LGr
SI_GATE: yes
T_TG_NM: 14.9
T_BG_NM: 21.4
TG_LIMIT: [−0.8, +0.8] V
BG_LIMIT: [−5.0, +5.0] V
SI_LIMIT: [−20, +20] V
B_CAP_T: 10.0
T_CAP_K: 100
TG_ADDR: GPIB0::1
BG_ADDR: GPIB0::24
SI_ADDR: ASRL7
BIAS_CHANNEL: sr1
LOCKIN_ADDRS: `sr0` GPIB0::22, `sr1` GPIB0::14, `sr2` GPIB0::19, `sr3` GPIB0::18
BIAS_R: 10 MOhm
DRIVE_FREQ: 13.777 Hz
SR0_GAIN: −1E6
CONTACT_LIVENESS: Alive: T_SD, L_1, L_2, L_3, L_4, B_SD. Dead: R_1, R_2.

## CONTACT_MAP

Hall bar. `T_SD` and `B_SD` are source and drain at the top and bottom
of the bar; `L_1`–`L_4` are voltage probes down the left side, `R_1`–`R_2`
the right. Only the provided configuration below is wired to instruments
this cooldown:

| Label | Pad | | Label | Pad |
|---|---|---|---|---|
| T_SD | 5 | | L_1 | 29 |
| L_2 | 13 | | L_3 | 45 |
| L_4 | 4,12 | | B_SD | 20,44 |
| R_1 | 1 | | R_2 | 11,27 |

## PROVIDED_CONFIG

| role | label |
|---|---|
| source | T_SD |
| drain (`sr0`) | B_SD |
| `sr1` (Rxx) | B_SD–L4 |
| `sr2` (Rxx) | L4–L1 |
| `sr3` (Rxx) | L3–L2 |

## NOTES

none
