**Read:** Calibration established. The CNP line is clean and straight across the full box; the fit tracks the argmax ridge by eye on both channels (Verify overlay: PASS).

- **Cap ratio (data-calibrated):** c_bg/c_tg = **1.309** (sr1), **1.300** (sr2) — agree to 0.7%, one calibration for the device. Matches the **geometry prior 1.300 to <1%** (Verify geometry-sanity: PASS). RMS ridge residual ~65–73 mV; 40/41 rows used (1 edge-clipped).
- **Absolute scale:** geometry prior (c_tg anchored on t_tg = 15.6 nm hBN, κ=3) → **two-tier provenance: ratio data-calibrated, scale geometry-prior (~10–15%), pending a QH lever-arm upgrade.**
- **(n=0, D=0) operating point:** V_tg = +0.087 V, V_bg = +0.066 V. **D=0 line** slope dV_tg/dV_bg = +1.309; reaches **≥ ±6×10¹² cm⁻²** within validators (BG ±4.5 binds near ~±12×10¹², so density is not the limiter) — ample range for SdH on both sides. `cal` and `gates_for(n, D)` are now the session calibration for downstream cells.

**Offset caveat:** the map puts n=0 at V_bg=+0.13 V (at TG=0) vs Gate C's +0.40 V — a **settling-lag difference** (~0.27 V ≈ 0.2×10¹² cm⁻²; expected, since each measurement's fast-axis lag biases the offset but not the slope). Used the 40-row map fit; n=0 location carries ~±0.2×10¹² cm⁻² until a bidirectional check or the Luttinger sum (Σf = n) pins it.

**Physics note (interpretation held):** CNP peak Rxx grows strongly with |D| — ~1.3 kΩ at D≈0 to ~100 kΩ at |D|≈1.1 V/nm (corners). A D-tunable CNP gap is *consistent-with* ABC (or small-domain ABC shunted by ABA), but per the investigation's domain/mosaic caveat this is **not** a standalone call — it feeds the per-channel SdH read, it does not pre-empt it.
