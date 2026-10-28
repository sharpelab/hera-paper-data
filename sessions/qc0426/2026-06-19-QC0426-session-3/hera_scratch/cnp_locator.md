## HERA — Step 1a: 1D CNP locator (cheap-first, E1 auto)

`cnp-and-dline-calibration` Step 1 needs a 0 T gate map that brackets the CNP, but the
CNP location is not on record (established fresh this session) and at the origin the device
is metallic (~1.3 kOhm, Gate C). Rather than commit ~1 hr of 2D map against an unknown CNP
position, this **~2 min** 1D linecut sweeps TG across its full validator range [-6, +7] V at
**BG = 0, Si = 0, B = 0**: the Rxx maximum locates the CNP in V_tg at V_bg = 0 — i.e. the
CNP-line **intercept** — confirming the CNP is inside the gate box and centering/sizing the
2D map to follow. Geometry prior on the slope is dV_tg/dV_bg = -c_bg/c_tg ~ -1.3 (15.6 nm TG
hBN / 12 nm BG hBN), so a CNP at TG=b (BG=0) sweeps to b∓1.3·4.5 = b∓5.85 V across the BG
range — inside the [-6,7] TG window for |b| small.

Preconditions asserted: sample_T < 5 K, |B| < 0.05 T, and a live-current check (mux selection
persists from Gate C). dwell 1.0 s (tau=0.3, 24 dB/oct; under the 7-10·tau settling floor but
benign for locating a smooth Rxx peak — the fan/spot-check will sit at the floor). 106 pts,
0.123 V/pt. Tags `cnp-and-dline-calibration`. Writes `data/<id>/`.
