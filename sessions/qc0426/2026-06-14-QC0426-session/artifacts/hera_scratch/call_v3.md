# Phase 2 — STACKING CALL (QC0426, this session)

**Device-level: ABC (rhombohedral) — strong** on the B=0 + single-particle evidence accessible at 1.2 K. *Decisive* confirmation (the ν=±6 QHE sequence and an LK single mass) needs lower temperature; everything reachable on this cooldown points ABC, across the whole device.

### 1. Per-region verdict (STYLE strength scale)
- **All 9 surveyed regions: ABC.** Every contact-pair region — top edge (T3–T4, T4–T5, T3–T5) and bottom edge (B4–B5, B3–B4, B4–B6, B3–B5) plus two transverse pairs — shows the D-gap. **No region is flat → no mosaic disagreement.**

### 2. Evidence (feature → coordinates → reference → artifact)
- **Device-wide displacement-field gap** (file_id 18, 22, 23; B=0): CNP Rxx grows **×26–505 with |D|** over D∈[−1.0,+1.15] V/nm in **every one of 9 regions**; minima ~0.1–1.3 kΩ (near the 250 Ω semimetal benchmark), maxima 19–220 kΩ. The ABC D-gap fingerprint device-wide (paper §discriminators / ABC contrast, ref. 5 Bao 2011). ana multi-region cell.
- **Single Fermi surface** (file_id 20 n=1–4, 21 n=3.5–10): one SdH frequency per n-column in the Nyquist-clean field window (0/N two-pocket at b-range (4,8)/(5,8)/(6,8) T), **and** the SdH lever-arm sum-rule — a single linear f(n) through the origin across n=0.6→10, one g=4 band carrying ~the full density (slope 85% of the g=4 ideal). Against ABA ML+BL two-pocket (recipe step 3.5). ana cells 18, 21 + lever-arm cell.
- **No ABA crossing chains** (file_id 21): N_M=1 (n≈6.8), N_M=2 (n≈10) model loci in-window — straight single-ladder ν-rays, no co-located curved arcs (forward model hera/models/aba_trilayer, ml_trajectories). ana cell 21.
- **Hall** (file_id 20): classical (Rxy≈B/ne, sloping) — no QHE plateaus → moderate mobility (onset ~2.5–3 T).

### 3. Confidence + hedges
Strong on accessible evidence; not decisive. Remaining hedges (all need lower T / interactions, not more B=0 or single-particle work):
- **No QHE plateaus** at this mobility/T → no ν=±6-centered (12-fold) test, the textbook ABC QHE clincher.
- **No LK-mass / temperature cross-check** of the single-band result (the decisive single-particle follow-up).
- Absolute n/D scale is SdH-anchored to ~15% (geometry-prior magnitudes ~15% high; ratio c_bg/c_tg=1.314 unchanged).

### 4. What would make it decisive
1. **Lower T (mK rig)**: QHE plateaus → ν=±6-centered sequence (ABC) and a quantized lever-arm; symmetry-breaking / ν=0 insulator vs |D|.
2. **Temperature-dependence (LK mass)** on one SdH branch here — single mass confirms single-band.

### 5. Status
**ABC (strong)** across the whole device, feature-cited, with the ABA discriminators (two-pocket, crossing chains) tested in-window and absent and the gap shown device-wide. The hold-back to *decisive* is purely a temperature/interaction limit (resolution ladder), not a fingerprint gap. Per the recipe's Next: ABC is the flat-band/correlated candidate — the physics deserves a low-T (mK) campaign; an LK-mass series here would firm the single-band leg before warming.
