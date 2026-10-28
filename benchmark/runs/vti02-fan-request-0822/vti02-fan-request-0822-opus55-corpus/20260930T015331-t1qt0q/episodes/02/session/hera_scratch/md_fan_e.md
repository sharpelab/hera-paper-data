## HERA — Step 4: Landau fan, electron side, D = 0 (`landau-fan-vti`, per `tetralayer-stacking-fs-count`)

**Why this fan.** Both spot checks show SdH, and each has the three-tone set the investigation warns about: two tones f₁, f₂ plus a third at their sum. Electron side (run 6, n = +3.2, F_L = 33.1 T): **7.3, 22.3 and 29.4 T**, where 7.3 + 22.3 = 29.6. Hole side (run 7, n = −1.2, F_L = 12.4 T): **6.6 and 12.3 T**. The run-6 set has two readings:
- an ABAB pair at global scale ≈ 0.89 (model: 7.3 / 25.8 T at scale 1) plus a breakdown sum tone;
- a 7.3 T fundamental with its 3× and 4× harmonics. This is the ratio trap the investigation names, and `sdh_onset` flags both upper tones as "~3×/~4×".

Only **n-dependence** tells them apart. Over this window the ABAB heavy branch runs 17→26 T (×scale), while 3× the partner runs 10.6→22.4 T. They coincide near n = 3.2 and are about 6 T apart at n = 2.0. The electron side is the side to fan: it reaches the design regime (n ≳ 2–3×10¹², where the templates separate). The hole side is capped at −1.27×10¹² by the TG −0.3 V limit, deep in the close, balanced-pair exception regime.

**Design** (numbers from run 6 `sdh_onset` on its 10 mT-sampled record, B ≥ 1 T):
- **B_lo = 1.0 T.** This is `onset_b` for the carrying 7.3 T tone. It is censored (still alive at the edge), so it is the recipe's floor. The 0.3–1 T part of run 6 was sampled at 50 mT, which undersamples a 7 T tone.
- **B_hi = 10 T.** This is the session cap. The heavy- and F_L-tone records (onsets 1.40 / 1.76 T) need the high-B half for the F_L-tone-origin B-window split.
- **d(1/B) = 0.0100 T⁻¹**, 91 rows, uniform in 1/B. That is one third of the Nyquist interval on F_L(3.25) = 33.6 T. Going only to plain Nyquist would fold the strong 2nd harmonics seen in run 6 (2 × 22 T) onto the heavy tone.
- **n = 2.00 → 3.25×10¹²**, 27 points (Δn = 0.048). That is 2.0 points per g = 4 ray period at B_lo, 2.8 at 1.4 T and 3.5 at 1.76 T.
- **Resolution δF:** 1.6 T for the heavy tone, 2.1 T for the F_L tone, 1.1 T for the partner.
- **Lock-in and settling**, the same as runs 6/7: sr1 50 µV = 5 kΩ full scale, τ 0.3 s / 24 dB, fast_delay 1.8 s (6τ), slow_delay 3 s (10τ after the flyback). The weak partner tone varies slowly in n (≥ 8 points per period), so the 6τ fast-axis lag barely reaches it.
- **Dynamic range:** the worst corner is n = 2.0 at 10 T. Expected R ≈ 73 Ω (B = 0, run 5) × the run-6 magnetoresistance factor of 9.5 × 1.5 low-n margin ≈ 1.1 kΩ, which leaves ≥ 4.5× headroom. Quantization is 0.19 Ω.

**Coverage trade:** the partner reaches the investigation's ≥ 5-period bar only for n ≳ 2.65 (it needs f ≥ 5.6 T with this record). Below that it gets 3–5 periods, so the partition check f₁ + f₂ = F_tone runs on 2.65–3.25. The heavy/F_L-tone n-tracks, which are the harmonic screen, run over the full window. Reaching the partner down to n = 2.0 would need B_lo ≈ 0.65 T. That costs a low-field extension to pin the censored onset first, plus about 50 more rows (~+1 h).

**Price** (from this session's runs 5–7: 0.13 s/pt read + gate overhead, 0.5 s magnet polling per step):
- grid 27 × 91 × 1.93 s = 79 min
- turnaround 11 min
- traverse 1 → 10 T 66 min
- pre-position 0 → 1 T 7 min
- **total ≈ 2 h 45 m**, ending at **10 T**, gates parked at 0. The LK ladder (Verify) rides the field down from there.

**Checkpoints:**
- **First rows** (t+10–15 min, B ≈ 1.0 T): Rxx in the run-6 range (10–60 Ω), no rail, gate currents at the pA offsets, T at base, field tracking the setpoints.
- **Periodic, interim per-column FFT on the landed rows:**
  - B ≈ 1.5 T (row 35, t+46 min): partner visible across columns.
  - B ≈ 2.5 T (row 61, t+79 min): heavy tone emerging and moving with n.
  - B ≈ 5 T (row 81, t+2 h): first track of heavy vs 3× partner.
- **Wash-out call:** if no column shows content above 10 T by 2.5 T, abandon (~1 h 25 m spent). The read is then resolution-limited on this rig.
