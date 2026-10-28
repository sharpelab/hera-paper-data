## HERA — Step 4: Landau fan (`landau-fan`) at D = 0, n = −1.20 → +3.20×10¹², B 1 → 10 T

**Why this, now (plan step 4).** Runs 6/7 established that this device oscillates
beautifully — R_xx minima reach ≈ 0 Ω on both carrier signs and `sdh_onset` tracks
tones down to 0.30 T (electron, n = +3.2×10¹²) and 0.71 T (hole, n = −1.2×10¹²),
peak SNR ~100. Both spot checks show **several tones** (electron: a carrying 7.1 T
plus 3.0/4.2/5.2/9.5 T and a 14.1/22.2/29.5 T ladder; hole: 6.6 T plus
4.7/8.5/9.4/12.3/14.8 T). At a *single* density that multiplicity is not
interpretable: a genuine second Fermi surface and a harmonic of the first look
alike. The stacking call turns on exactly that distinction — **one** Fermi surface
carrying the full density (F = |n|h/4e) is rhombohedral-like ABCA, **two** with
F₁+F₂ = F_full is Bernal-like ABAB, two unequal + D-asymmetric is ABCB. Tracking
F **versus n** separates them: a real pocket has its own dF/dn and its own
intercept at the CNP, a harmonic keeps an exact integer ratio. The same map gives
the second, FFT-independent read — the Landau-level gap slopes dn/dB = ν·e/h,
i.e. the degeneracy sequence and whether two families interpenetrate and cross.

**Grid.** Fast axis is the **D = 0 line** with (V_tg, V_bg) co-swept
(`multimegasweep`): n = −1.20 → +3.20×10¹² cm⁻², 177 pts, Δn = 0.025×10¹². Those
endpoints are the ones runs 6/7 already sat at — V_tg −0.2770…+0.9836 V (23/16 mV
inside the committed limits), V_bg −0.4650…+1.1661 V. Slow axis is **B = 1.0 →
10.0 T, 71 rows uniform in 1/B** (`field_invB`), which hands the per-column FFT an
already-even 1/B record: Δ(1/B) = 0.01286 ⇒ F_Nyquist = 38.9 T, clear of
F_full(3.2×10¹²) = 33.1 T, and δF = 1.11 T over the full window. Ascending, so the
fan ends at 10 T and step 5 (the D axis) rides the magnet back down — no
re-traverse.

**Coverage trade, stated.** (i) The fan starts at **1 T, not at the 0.3 T onset**:
below 1 T the 4-fold LL spacing at the top density is < 0.1×10¹² (< 4 points), so
lower rows would add cost without readable n-structure — and runs 6/7 already
cover 0.3–1 T densely at two densities for the low-field FFT. Extending to 0.5 T
at the same 1/B spacing would cost ~78 extra rows (≈ +4.5 h). (ii) **D = 0 only**;
the D axis (discriminator 3, and the ABCB ±D asymmetry test) is step 5, riding
down from 10 T. (iii) Only `sr1` (B_1–B_2) is wired for R_xx and sr2/sr3 are n.c.
— **no Hall channel**, so ν comes from fan slopes and SdH frequencies, never from
R_xy plateaux. That is a standing session limitation, not a choice here.

**Sensitivity — 100 µV (10 kΩ FS at 10 nA), the judgement call.** Largest R
measured anywhere on the D = 0 line is 587 Ω (run 7 at 10 T) and the 0 T CNP peak
at D = 0 is ≈ 330 Ω, so 10 kΩ is 17–30× the known worst case while keeping the
electron-side oscillation amplitude (±50–100 Ω) at 0.5–1 % of full scale, the band
runs 0–3 showed readable. The run-4 lesson (size for the *ridge at max |D|*)
does not bite here: this fan sits at D = 0, where the CNP is least gapped. Residual
risk is a strongly insulating ν = 0 at high B railing **the one or two columns at
the CNP** — that would still be informative (R > 10 kΩ is a lower bound) and costs
2 of 177 columns. A `CLIP` counter prints if any point exceeds 0.9 FS.

**Preconditions checked in-cell** (assumed, not set): thermometry logfile
advancing; T_sample 1.0–1.5 K; |B| < 0.05 T (the fan ramps itself to 1 T);
V_si = 0; gates at 0; Keithley nplci = 1; persistent switch on and output enabled.
Leak guard trips the sweep at |I_gate| > 1 nA. Gates park at 0 on exit (including
on interrupt); the field is deliberately **left at 10 T**.

**Price.** Calibrated on run 5 (4158 pts / 4873 s = 1.172 s/pt at fast_delay 1.0 s,
same followed set and nplci): 71 rows × (177 × 1.172 s + 3.5 s gate flyback + 3 s
slow_delay) = 4.2 h, plus the 9 T magnet traverse at 0.137 T/min = 66 min and
71 × 3 s of settle ⇒ **≈ 5 h 20 m, call it 5 h 50 m** with this rig's observed
5–10 % overrun on long runs. Lock-in τ = 0.3 s at 24 dB/oct ≈ 1.2 s of filter
memory against 1.172 s/pt, so each row carries a ≈ 0.8-point lag in n — constant
and single-direction, so it displaces the fan's apex, not the slopes ν that carry
the physics.

**Checkpoints** (`hera-watch` digests, armed with the cell): **first rows** at
B ≈ 1.00–1.05 T — R range sane vs runs 6/7, no clip, leakage at the pA floor,
field readback tracking setpoints; **≈ row 25** (B ≈ 1.5 T) and **≈ row 50**
(B ≈ 2.9 T) — re-form the partial fan and check that LL minima are emerging with
resolvable slopes. Abort conditions: leak trip, sustained clipping away from the
CNP, or no LL structure resolvable by 3 T (then the fan is n-resolution-limited
and the read reverts to fixed-n 1/B traces at a ladder of densities).
