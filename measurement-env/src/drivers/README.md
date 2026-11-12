# drivers — instrument drivers (source of truth: this repo)

Custom QCoDeS drivers for the lab's rigs. **As of 2026-06-11 this
directory is the source of truth** — it is no longer a read-only vendored
mirror of the rig working tree. Edit here; syncing the rig PC's separate
install / the upstream `dgglab/VTI-drivers` repo is handled out of band
(Zack).

Renamed from `src/vti_drivers/` (2026-06-11). Deployments whose
notebooks import `vti_drivers.*` need the import lines updated to
`drivers.*` on their next env sync — the measure templates in this repo
are already updated.

## Contents

- VTI rig drivers: `FastBi1K5` (magnet), `SRS_DC205`, `Lakeshore_218`/
  `Lakeshore_335`, `AMI_420`/`AMI_1700`, `Terranova_906A`, `QSwitch`.
- House additions (never existed in the rig tree): `contact_mux` —
  QSwitch-backed contact-pair switching with truthful
  `measurement_config` fragments; `qdac` (`bring_up_qdac_gate`, the
  QDAC-II gate bring-up) over the vendored `QDAC2` driver.
- `QDAC2.py` — the QDevil QDAC-II driver vendored verbatim from
  `qcodes_contrib_drivers` (see "QDAC2 driver" below).
- `setup.py` is the rig's old editable-install manifest, kept for
  reference only; this directory is exposed as the `drivers` package
  through measurement-env's build config.

## Planned consolidation

The toploader drivers currently live in `src/sharpelab_nb/drivers/`
(`srs_dc205`, `yokogawa_7651`, `anc350`, `lockin_servo`); the intent is
a single `drivers/` package for both rigs. The fold-in is deferred
because it is not a pure move: `SRS_DC205.py` (VTI) and `srs_dc205.py`
(toploader) **collide on Windows case-insensitive filesystems**, and the
two implementations have deliberately different ramp semantics — VTI's is
rate-based (`ramp_rate` V/s, gate-safe dV/dt at any move size); the
toploader's is fixed-duration (~1 s + a mandatory 10 s settle on moves
> 0.1 V). They are not interchangeable, so merging them needs a rename
plus a semantics decision, not a `git mv`.

## QSwitch driver choice

`QSwitch.py` (the rig fork, v0.5.0 lineage) is kept over
`qcodes_contrib_drivers` 0.23.0's QDevil driver: it is the newer code —
modern qcodes import paths (the contrib copy emits
`QCoDeSDeprecationWarning` on import), an added `unground()`, and a
`ground()` that also opens all breakout taps — and it is the driver with
live history on the VTI rig (Bingcheng's CF01B1 campaign ran it against
QSwitch firmware 2.0). Re-evaluate if `qcodes_contrib_drivers` ships a
newer QDevil driver than the fork.

## QDAC2 driver

`QDAC2.py` is the QDevil QDAC-II driver vendored verbatim from
`qcodes_contrib_drivers` v0.24.1 (MIT, © 2019 QCoDeS). It is self-contained
(numpy / qcodes / pyvisa / packaging). To update, re-vendor the single file
rather than re-adding the `qcodes-contrib-drivers` dependency (a banned dep —
see `banned_deps_test.py`).

## Provenance (historical)

- **Vendored**: from the rig working tree at
  `dgg-vti:~/Documents/GitHub/vti_drivers/` (Windows lab PC `dgg-vti`,
  user DGG), copied via scp on **2026-06-09**.
- **Upstream repo**: `dgglab/VTI-drivers` (installed editable into the
  rig's system Python, package name `VTI_drivers`).
- **Rig git HEAD at copy time**: `5859dad04a5735199927e225dcd3e69e8f2a24b6`
  ("minor edits to lakeshore335", 2025-11-06); the working tree was
  newer than HEAD:
  - locally modified (tracked): `AMI_420.py` (mtime 2026-02-14),
    `SRS_DC205.py` (mtime 2025-11-21)
  - untracked (not in upstream at all): `FastBi1K5.py` (mtime
    2026-02-26), `QSwitch.py` (mtime 2026-04-24), `async_station.py`
    (mtime 2026-01-12)
  - unmodified vs HEAD: `AMI_1700.py`, `Lakeshore_218.py`,
    `Lakeshore_335.py`, `Terranova_906A.py`

## Usage

Imports are package-qualified (the rig's old editable install used flat
top-level imports; we differ deliberately):

```python
from drivers.FastBi1K5 import FastBi1K5
from drivers.SRS_DC205 import SRS_DC205
from drivers.contact_mux import ContactMux
```

Both rigs build the measurement station from the sharpelab measureme
fork (`lib/measureme`) — `s = sweep.AsyncStation(meas_config)`.
