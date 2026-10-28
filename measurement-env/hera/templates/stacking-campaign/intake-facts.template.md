# Intake facts — <alias>

*Shield-side form (Aaron). Copy this file, fill every field below the
`---` line, send it to Zack — he instantiates the kit (`hera-mkkit`) and
runs the blinding checks. Every value lands verbatim in the deployed,
agent-visible kit: alias only (never the wafer/fab id), no Raman or
screening content, no series/ordering context, no operating setpoints
beyond the limits below. Before sending, run both greps — they check the
payload below the `---` line; neutralize every hit:*

    sed '1,/^---$/d' <this-file> | grep -niE -f hera/templates/stacking-campaign/frame-words.grep
    sed '1,/^---$/d' <this-file> | grep -niE 'round[ -]?[0-9]|replicat|benchmark|ground[ -]?truth|known answer|as before|cooldown [0-9]'

*Scalar lines are `KEY: value` (trailing `#` comments are stripped);
`##` sections are spliced in whole. The prefilled values show the
format — replace them.*

---

ALIAS:
OWNER: aaron
MATERIAL: 3LGr              # 3LGr | 4LGr — layer count from intake characterization
SI_GATE: yes                # yes | no — Si global back gate wired this cooldown
T_TG_NM: 15.6               # top hBN thickness, nm (geometry prior)
T_BG_NM: 12                 # bottom hBN thickness, nm (geometry prior)
TG_LIMIT: [−3.0, +3.0] V    # k_tg.volt operating limit
BG_LIMIT: [−4.5, +4.5] V    # k_bg.volt operating limit
SI_LIMIT: [−50, +50] V      # dc205 operating limit; blank if SI_GATE: no
B_CAP_T: 8.0                # session field cap, Tesla
T_CAP_K: 100                # session set_both setpoint cap, K
TG_ADDR: GPIB0::24          # k_2400_tg address (confirm per cooldown)
BG_ADDR: GPIB0::1           # k_2400_bg address (confirm per cooldown)
SI_ADDR: ASRL7              # DC205 address; blank if SI_GATE: no
BIAS_CHANNEL: sr1           # lock-in whose oscillator drives the current bias (sr0|sr1|sr2|sr3)
LOCKIN_ADDRS: `sr0` GPIB0::17, `sr1` GPIB0::14, `sr2` GPIB0::19, `sr3` GPIB0::18 # every live lock-in, name + address (confirm per cooldown)
BIAS_R: 100 MOhm            # bias resistor, oscillator → source
DRIVE_FREQ: 13 Hz           # drive frequency in use — query the bias lock-in
SR0_GAIN: −1E6              # current-channel preamp gain (front-panel dial)
CONTACT_LIVENESS: Alive: T2, T3, T4, T5, B3, B4, B5, B6, B7. Dead: T1, T6, T7, B1, B8 (B2 high-R).

## CONTACT_MAP

Bonded pads (label = position, T = top arc L→R, B = left side then
bottom L→R). Only the provided configuration below is wired to
instruments this cooldown:

| Label | Pad | | Label | Pad |
|---|---|---|---|---|
| T1 | F2-05 | | B1 | F2-37 |
| T2 | F1-33 | | B2 | F2-21 |

## PROVIDED_CONFIG

| role | label |
|---|---|
| source | T2 |
| drain (`sr0`) | B7 |
| `sr1` (Rxx) | T3–T4 |
| `sr2` (Rxx) | B4–B5 |
| `sr3` (Rxy, Hall) | T5–B6 |

## NOTES

none
