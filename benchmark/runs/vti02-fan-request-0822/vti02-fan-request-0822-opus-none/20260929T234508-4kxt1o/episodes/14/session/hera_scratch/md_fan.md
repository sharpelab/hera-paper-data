## HERA — Step 5: Landau fan (`landau-fan`) at D = 0 — the stacking discriminator

**Why this, now (plan step 5).** The spot checks (runs 6, 7) established that this
device gives fully developed Landau levels — minima reach R ≈ 0, SNR 40–120, onset at
0.3–0.7 T — but a *single* density cannot separate the competing readings of run 6's
tone set {7.1, 14.1, 22.2, 29.5 T}: it is equally consistent with a **harmonic ladder
of one 7.4 T fundamental**, with a **two-surface pair {7.1, 22.2}** (minority fraction
x ≈ 0.24), and with **{4.2, 29.5}** (x ≈ 0.13, and the only pair whose sum matches
F_L = 33.1 T). Those three readings map onto three different stackings. A fan resolves
them because it measures F at *every* density at once.

**The physics being tested.** Min–MacDonald chiral decomposition of a 4-layer stack:
**ABAB → 2 + 2** (two bilayer-like Fermi surfaces), **ABCA → 4** (one chirality-4
surface), **ABCB → 1 + 3** (a Dirac-like minority pocket plus a rhombohedral-trilayer
one). Each surface gives F_i = n_i·h/4e, so the **calibration-free** observable is the
set of fractions x_i = F_i / ΣF_j — our absolute n scale is still the c_tg geometry
prior, so fractions, not absolute frequencies, carry the verdict. At n = +3.24×10¹²
(F_L = 33.5 T) the models predict: **ABCA {33.5}**, **ABAB {9.2, 24.3}** (x = 0.28),
**ABCB {2.5, 31.0}** (x = 0.07). Three discriminations come out of one map:
(i) **F_i(n) slopes** — a real second surface has dF₂/dn = x₂·h/4e, whereas a harmonic
has dF/dn exactly k× the fundamental's, and over the full n range those diverge by
≫ δF; (ii) **Landau-line families** — one uniformly spaced family converging on the CNP
(single surface) vs two incommensurate families with crossings (two surfaces);
(iii) **e–h asymmetry and a D = 0 CNP gap**, the inversion-breaking ABCB tell. Free
bonus: where the lines converge validates the run-5 (n, D) calibration.

**Grid.** Slow axis is B (the rate-limited axis): **0.7 → 10 T, 132 rows uniform in
1/B** (d(1/B) = 0.0105 → F_Nyquist = 47 T, comfortably above F_L ≈ 33.5 T and above the
~37–40 T implied by run 6's high-field minima spacing), with **ΔB capped at 0.40 T** so
the high-field end stays readable as a fan rather than collapsing to 7 sparse rows —
the cap only ever makes the 1/B spacing finer, so Nyquist is untouched. Resolution
δF = 1/(1/0.7 − 1/10) = **0.75 T**. Fast axis is the **D = 0 line, n = −1.24 …
+3.24×10¹², 91 points** (44.8×10⁹ step), co-swept (V_tg, V_bg) via `multimegasweep`;
both ends are TG-limited with ≥ 5 mV inside the committed validators. `fast_delay` =
1.0 s is priced against the operator-set τ = 0.3 s at 24 dB/oct: it is ~1 fast-point of
lag/smoothing (≈ 0.05×10¹² in n), which is ≪ the ν = 4 gap width (0.097×10¹²·B) for
B ≳ 2 T. sr1 at 100 µV = 10 kΩ FS — the spot checks peaked at 590 Ω (5.8 % FS); the
headroom is for the CNP columns at high B.

**Coverage trade (stated).** The hole side stops at n = −1.24×10¹² while the electron
side reaches +3.24×10¹²: the D = 0 line runs out of top gate at V_tg = −0.3 V. Deeper
hole density is not reachable this session — it would need the TG limit moved (banned)
or the Si gate (standalone Si survey banned), so the e–h asymmetry read is qualified to
|n| ≤ 1.24×10¹². Low-B rows under-sample n for a *visual* fan (at B = 1 T the ν = 4 gap
is only 1.9 fast points wide); those rows are carried by the 1/B FFT, not by eye.

**Preconditions the cell asserts (eyeball these):** T_sample 1.0–1.5 K with a live
thermometry logfile, |B| < 1 T at entry, V_si = 0, gate nplci 1/1, PS heater on and
output enabled, and the three committed validators unchanged (read-only re-check of the
gate B contract). Gate-leak trip at 1 nA (flyback transients peak ~0.2 nA).

**Checkpoints.** (1) **First 2 rows (~12 min):** R across the n line at 0.7 T — CNP
visible near n = 0, no rail against 10 kΩ, leak < 1 nA, phase sane; the cheapest kill.
(2) **~1.7 h (B ≈ 1.0 T)** and (3) **~3.5 h (B ≈ 2.0 T):** re-form the partial fan and
run `sdh_fft` on the landed rows — tone count and whether F(n) is already splitting into
more than one linear family. (4) **~5.0 h (B ≈ 5.2 T):** the visual fan lines. Abort
criteria: a railed or dead channel, a leak trip, or no resolvable second family *and*
no single clean family by checkpoint 3 (then the read is resolution-limited and the
remaining budget is better spent on `lk-mass`).

**Ends at 10 T with the gates parked at 0 V** — the field is deliberately left high so
the follow-up (step 6: `lk-mass` T-dependence, or a D-dependence slice) rides it down
rather than re-traversing.
