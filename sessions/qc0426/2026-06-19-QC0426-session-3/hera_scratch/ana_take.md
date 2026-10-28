### Take — Step 1 (n, D) calibration (runs 0, 1)

**CNP located and the (n, D) conversion is live.** Run 0 (1D TG locator at BG=0) put the CNP
near V_tg ~ +0.2-0.4 V; run 1 (0 T TG-BG map, 17x105) gives the precise CNP line from the
ridge centroid on both Rxx channels:

- **V_tg = -1.2923 * V_bg + 0.149** ; ratio **c_bg/c_tg = 1.292** (sr1 1.295, sr2 1.290 — agree
  to <0.5%, one device calibration), matching the geometry prior 1.300 to 0.6% (the happy case
  of the geometry-sanity check).
- Calibration: c_tg = 1.703e-3 F/m^2 (geometry anchor), c_bg = 2.200e-3 F/m^2 (from the fitted
  ratio), n_offset = -1.58e15 m^-2, D_offset = 0 (assumed — no feature physically locates D=0).
  Closure exact (|n|<1e-15 along the ridge).
- **Two-tier provenance: ratio data-calibrated; absolute n/D scale geometry-prior** until a
  quantum-Hall lever-arm check (dn/dB = nu e/h) upgrades it.

**Device quality:** leakage clean (BG 0.24 nA, Si 0.59 nA across the whole map). Both Rxx pairs
(sr1 T3-T4, sr2 B4-B5) stay **metallic (~50-70 Ω)** across the full D~0 n-window (-11.4 .. +11.0
e12 cm^-2) — no insulating arms; both are usable for the fan/spot-checks. sr3 (Rxy) ~0 at B=0.

**One stacking-relevant observation (held lightly, not a call):** the CNP resistance is **low at
D~0 (~1 kΩ)** and rises with |D| (clipping the 2e-5 sensitivity at the high-|D| map ends). A
CNP that caps low at D~0 is *consistent-with* small-domain ABC shunted by ABA (or with ABA), and
is explicitly **not** decisive per the investigation's domain/mosaic caveat — the FS-counting
route (SdH spot checks -> fan) is the actual discriminator and does not rest on this. Flagged for
the per-channel read; a quantitative CNP-R(D) at higher sensitivity is a later (Step 6) option.

**Next:** Step 2/3 — SdH spot checks at large hole and large electron density at D=0.
