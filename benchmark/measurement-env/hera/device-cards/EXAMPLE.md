# Device card — EXAMPLE (not a real device)

*Device cards are per-device state. They live in the measurement directory
alongside the working notebook (e.g.
`~/measurements/<user>/<device>_toploader/device_card.md`), not in this repo.
This file is an example/template only; copy and edit it for a real device.*

---

## Identity
- **Device id**: `EXAMPLE` *(the directory name under `~/measurements/<user>/`)*
- **Material**: rhombohedral pentalayer graphene + hBN encapsulation, no TMD
- **Owner**: aaron
- **Status**: hypothetical / for reference only

## Gate stack
- **Top hBN thickness** (`t_tg`): 16 nm
- **Bottom hBN thickness** (`t_bg`): 25.5 nm
- **Si back gate**: yes (300 nm SiO₂ + degenerate Si).
- **hBN dielectric constant** (`ep`): 3
- **Single device or dual**: single

## Validators (current cooldown)
*Initial values are geometry-derived ceilings (`±0.5 V/nm × thickness`), not
safe ranges; `gate-current-sanity-check` blesses real ranges per cooldown.*

- `k_tg.volt`: ±8.0 V *(initial; not yet swept)*
- `k_bg.volt`: ±12.0 V *(initial; not yet swept)*
- `k_si.volt`: ±48 V

## Known operating points
*Carried forward from prior cooldowns or earlier sessions. Re-verify before
relying on them — same device, different cooldown, different actual numbers.*

- Cooldown 3 (warmed up 2026-04-15, recooled 2026-04-22): `V_si = +48 V`
  worked well; SC dome at `(n, D) ≈ (0.55, 0.31)`; CNP line at
  `Vbg ≈ 1.4 × Vtg + 0.05`.

## Contact map
*If documented; otherwise mention "not documented in this card".*

- Source-drain: contacts 4–28 (28 = drain, 4 = source) for the canonical
  `mc_1` config; lock-in 4 reads `I_{30-21}`.
- Probe geometry: not documented in this card; see notebook `mc` definitions.

## Notes
*Free text — recent interventions on this device, fab particulars, anything
HERA should know that doesn't fit above.*

- This is an example file. Do not prime HERA with it; it doesn't describe a
  real device.

## What this card does not carry

*Rig / instrument facts (magnet, thermometry, equipment, addresses,
drivers) → rig card; recipes in play, the goal, the blocklist → brief;
general physics / analysis method (lever-arm formulas, reprojection) →
recipes.*
