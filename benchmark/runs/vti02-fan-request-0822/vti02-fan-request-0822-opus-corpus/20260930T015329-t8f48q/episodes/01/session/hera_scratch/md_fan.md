## HERA — Step 4: Landau fan (`landau-fan-vti`), electron side, D = 0, n = 3.20 → 1.00×10¹², B 1.0 → 8.0 T

**Why this fan, and what it has to settle.** Runs 6/7 (spot checks, ana below) both
resolve a **two-tone** set whose sum sits at ≈ 0.88 · F_L — one global density rescale,
the same on both carrier signs, inside the lever-arm prior. Electron side (n = +3.2×10¹²,
F_L = 33.1 T): tones at **7.3 T** and **22.0 T**. Hole side (n = −1.2×10¹², F_L = 12.4 T):
**4.9 / 7.4 T**, heavy fraction 0.64 — the model's hole-side ABAB partition to three
digits. That is an ABAB-shaped read. **But the electron pair's ratio is 22.0/7.3 = 3.01**,
and 14.4 T and 28.9 T are present too: the set is equally readable as a 1×/2×/3×/4×
harmonic comb of a single 7.3 T fundamental — the exact confound the investigation names
("the ABAB pair's ratio ≈ 2.6 drifts through 3× with density, and a ratio-only screen eats
the real heavy tone exactly there"). One column cannot decide it. **The n-dependence can:**
a harmonic tracks 3·F₁(n) at every density; a real pocket closes f₁(n) + f₂(n) = F_L(n)
across the fan (algebraic, model-free) and tracks its own Onsager curve. That is this fan's
job, plus Step 5's branch labeling against the forward model.

**Side: electron.** No side prior, so both were spot-checked. The electron side wins on
every axis — it reaches |n| = 3.2×10¹² vs the hole side's gate-limited 1.27×10¹² (the
D = 0 line hits the TG −0.3 V limit there), so only the electron side lives in the
investigation's design window (|n| ≳ 2–3×10¹²) where the templates separate; onset ≤ 1.0 T
vs 0.71 T with SNR ~100 either way; and the model puts the hole side at partition
0.485/0.515 at its density ceiling — the "close and balanced near-CNP pair" exception
regime the investigation says to design *around*.

**Design numbers (computed, `hera_scratch/fan_design.py`).**
- **Slow axis uniform in 1/B** — `field_invB(1.0, 8.0, 89)`, Δ(1/B) = 9.94×10⁻³ T⁻¹
  (10 mT steps at the low edge, 589 mT at the top). This is the per-column-SdH-FFT grid the
  base recipe prescribes, *not* the spot check's uniform-B: a fan row costs a whole 48-point
  gate line (~110 s), so rows are the expensive thing here, not the ramp — uniform-1/B buys
  the same Nyquist in **89 rows instead of 501**. Alias-free to **50.3 T**, clearing F_L(n_max)
  = 33.1 T and the 4× comb member at 29 T. Δ(1/B) at the low edge is exactly the spot check's,
  inherited as the recipe asks.
- **B_lo = 1.0 T** = `sdh_onset` on run 6's well-sampled leg: the 7.3 T carrying tone is
  **censored at the record's low edge**, so 1.0 T is a lower bound on the onset, and it is
  also the cheap end of the trade (ΔB ∝ B_lo², and the n-axis ray-Nyquist floor ∝ B_lo).
  The sub-1 T leg of run 6 is *not* evidence of a lower onset — at 50 mT steps its Δ(1/B)
  = 0.069 aliases everything above 7 T.
- **B_hi = 8.0 T.** δF = 1/(1/B_lo − 1/B_hi) = **1.14 T**, so splits above 2δF = 2.29 T are
  trustworthy. The binding separation is |F₂(n) − 3·F₁(n)| from the model's F(n) table — it
  narrows monotonically with density to **3.87 T at n = 3.2×10¹²**, clearing 2δF at every
  column. Going on to 10 T buys δF 1.14 → 1.11 T for +20 min and drags the n = 3.2 column's
  huge light-pocket quantum-limit feature (R: 0 → 520 Ω above 7.5 T, run 6) into the
  background-subtraction window.
- **Fast axis: 48 columns, n = 3.20 → 1.00×10¹² at D = 0**, Δn = 0.0468×10¹². Ray spacing
  g·(e/h)·B_lo = 0.0967×10¹² → **2.07 points/ray**, just over the ≥ 2 floor. (V_tg, V_bg)
  = (+0.9836, +1.1661) → (+0.3533, +0.3506) V; TG headroom to its +1.0 V limit is **16 mV**
  at the high-n end. Both gate columns move together — a paired n-line, not a frozen gate.
- **Dwell: `fast_delay = 2.1 s` = 7τ** at the read-back τ = 0.3 s / 24 dB/oct — the settling
  floor, not the base recipe's generic 4τ, because the n-axis is the fast axis under a
  per-column FFT read. `slow_delay = 1.0` on top of the magnet's blocking ramp + 3 s settle.
- **Sensitivity: 50 µV fixed** (5 kΩ full scale at 10 nA) — the spot checks' setting,
  inherited. Worst corner is low-n × high-B: R(n = 1.0×10¹², B = 0) = 116 Ω from the run-5
  gate map, ×10 measured MR (run 6) ≈ 1.2 kΩ, and ×20 for the MR growth toward the CNP still
  only reaches ~45 % of full scale. Both spot checks peaked at ~330–370 Ω below 8 T. Headroom,
  not precision: a railed column is unrecoverable, a coarse one is not.

**Coverage trade, stated.** This fan is the electron side only, n ≥ 1.0×10¹², B ≥ 1.0 T.
Excluded: the hole side (a mirror fan is ~4 h more and lands in the exception regime — it is
a *firming* measurement, not a deciding one); n < 1.0×10¹² (the light tone falls to 0.57 T
at n = 1.0, below δF — unresolvable at any window this device supports, and the near-CNP
columns are where all three stackings converge); B < 1.0 T (unmeasured onset, and each 0.1 T
of extra reach costs rows quadratically and tightens the n-axis floor).

**Preconditions the cell asserts** (state it assumes but does not set): thermometry logfile
advancing, T_sample 1.0–1.5 K, both heater ranges 0, V_si = 0, magnet at ≈ 0 T with PS heater
on and output enabled, gate NPLC = 1, and the whole (V_tg, V_bg) line inside the committed
validators. It positions the magnet to 1.0 T (≈ 7 min, blocking) before the station is built.

**Price: ≈ 4 h 05 m** — grid 89 × 48 × 2.27 s = 2.69 h, traverse 7 T at 0.137 T/min = 0.85 h,
row settle + flyback 0.09 h, +8 % over-run, + 7 min positioning. Per-point time is calibrated
on **this session's run 5** (63 × 66 gate map, `fast_delay = 1.0`, 4873 s → 1.172 s/pt
including row turnaround), not on inherited constants.

**Checkpoints.** (1) **First rows** (~4 min in, B = 1.00–1.02 T): sr1 not railed and not flat,
R along the n-line matching the run-5 B = 0 anchor (55 → 116 Ω, 3.2 → 1.0×10¹²) modulo
low-field MR, drain current ≈ 10 nA, |I_tg|, |I_bg| ≪ 1 nA, field readback tracking setpoints,
T at base. Abort there — the cheapest kill is in the first minute. (2) **~row 30 (≈ 1 h 20 m,
B ≈ 1.45 T)** and **~row 60 (≈ 2 h 45 m, B ≈ 2.4 T)**: per-column FFT on the landed rows —
by row 60 the record is 1.0–2.4 T (δF ≈ 1.7 T), enough to see whether the 7 T and 22 T tones
are present and whether their ratio moves off 3.00 as n falls. Wash-out call if no oscillation
content has appeared in any column by row 60 with R flat. A hard leak guard trips the sweep at
|I_gate| > 1 nA.
