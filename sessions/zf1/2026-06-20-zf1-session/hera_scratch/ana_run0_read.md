**Read — Gate C PASS.**
1. **Device alive** — current channel pinned at I_bias = 40 pA across the full BG range → passes full bias current, R_device ≪ 100 MΩ (current-bias regime, as the rig's bias network implies).
2. **4-terminal Rxx (sr3, 30-31) live and responsive** — smooth CNP peak 657 Ω at k_bg ≈ 0, ~13 Ω in the metal.
3. **Not a grounded short** — sr2/sr3 ranges differ 37× and both peak at the CNP (the b1c2 shared-contact-30 grounded-short failure mode is absent here).
4. **Leakage < 45 pA** across the BG validator (nplci=10, pA-resolved) — clean.
5. **CNP recon:** at k_tg = 0 the CNP sits at k_bg ≈ 0 to +0.1 V — one point on the CNP line; the map will give the slope.

**Caveat (drive level).** AC drive is 40 pA (sine 4 mV), **not** the device card's stated 0.1 V → 1 nA. The 4T Rxx noise floor is ~68 Ω, so the low-Rxx regime — exactly where SC candidates live (~13 Ω metal) — is buried in noise (see the 4T panel: only the CNP spike rises above the floor). **Drive bumped to ~0.5 nA (0.05 V) before the candidate-ID map** to bring the noise floor to ~5 Ω. sr4 (5-30) is unusable (shares the drive contact 5; ±24 kΩ scatter) — sr3 is the Rxx channel going forward.
