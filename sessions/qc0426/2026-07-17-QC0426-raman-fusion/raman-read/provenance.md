# QC0426 Raman data — provenance (as currently known)

- **Device**: QC0426, trilayer-graphene (N = 3 per fabrication records)
  dual-gated hBN-encapsulated device. No independent AFM/optical
  layer-count map was supplied alongside this file.
- **File**: `/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip` —
  WITec Project file supplied by the sample grower, received 2026-07-17.
  Readable via the `raman_stacking` tool's `load_wip()` (optional `witio`
  package).
- **Contents** (from file metadata, no spectral analysis performed):
  - `Spot1--Spec.Data 1`: single spectrum, 30 s, in-fiber power 4.0 mW,
    2026-05-14.
  - `Scan LA--002--Spec.Data 1`: 61×61 px over 20×20 µm, 13 s/pt,
    in-fiber 4.1 mW, ~5.9 h.
  - `Scan LA--004--Spec.Data 1`: 51×51 px over 20×20 µm (different scan
    center), 11 s/pt, in-fiber 6.0 mW, ~10.4 h, 2026-05-15.
  - Two video images (2240×1680 RGB) with per-pixel µm coordinate grids in
    the stage frame (same frame as the scan position grids), plus a
    1578 cm⁻¹ sum image and cursors/transformations.
  - Spectral axis: −891 to 3652 cm⁻¹, 2000 pts, all datasets. Excitation
    532.34 nm; 600 g/mm grating; 100×/0.9 objective.
- **Laser power at sample: NOT recorded** — only in-fiber values
  (4.0–6.0 mW); fiber/objective losses unknown.
- **Acquisition stage in the build sequence: UNKNOWN, pending the
  grower's answer.** Acquisition dates 2026-05-14/15. Whether the maps
  were taken on the bare flake, mid-stack, or the finished device is not
  yet documented.
- Spot size: not recorded (100×/0.9 at 532 nm → diffraction-limited
  ~0.4 µm expected).
