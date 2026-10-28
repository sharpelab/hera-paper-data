## HERA — Step 4: Landau fan at D = 0, electron side (`landau-fan-vti`) — the stacking call

**Why this fan, and why the electron side.** The spot checks are analysed (ana
notebook, runs 6/7). Run 6 (electron, n = +3.2e12, D = 0) resolves a **tone pair
at 6.9 T and 21.9 T** plus weaker content at 14.1 T and 29.5 T. Read as the ABAB
template that pair partitions F_L at 0.24 / 0.76 and sums to 28.8 T against
F_L = 33.1 T — a global density scale of **0.87**, inside the 0.8–1.2 lever-arm
band the investigation allows, and sitting on the forward model's ABAB pair at
this density (7.3 / 25.8 T, fraction 0.22). The 29.5 T tone is then the
symmetry-allowed inter-block **breakdown sum-tone** near F_L, and 14.1 T the
partner's 2nd harmonic. The competing reading is a pure **harmonic comb** on a
6.9 T fundamental (ratio 21.9/6.9 = 3.17 — the investigation's named trap, where
a ratio-only screen eats the real heavy tone); that reading forces a single FS
carrying n = 0.67e12 against a gated 3.2e12, i.e. scale 0.21, far outside the
band. Neither reading is settled on one column — **the n-dependence is the
discriminator**, and that is exactly what a fan measures.

Side is forced, not preferred: at D = 0 the `k_tg` operating limit (−0.3 V) caps
the hole side at **n = −1.28e12**, so the hole side can never reach the
investigation's |n| ≳ 2–3e12 design window where the templates separate. Run 7
(n = −1.2e12) sits in the named near-CNP hole exception regime (model pair
5.9/6.5 T — balanced and beat-like). The electron side reaches +3.26e12 and
already shows the resolved pair. Electron side it is.

**What the fan decides.** Per column, FFT in 1/B and track each tone vs density:
the ABAB partner fraction *curves* (0.09 → 0.22 over n = 1.2 → 3.2e12) while a
harmonic sits at exactly heavy/3 at every density. The two predictions separate
by 1.5 δF at the top of the window and **2.2–3.0 δF below n = 2.3e12**, where the
test also runs by absence: at n = 1.45e12 the harmonic hypothesis demands a
clearly resolvable 4.4 T tone (2.2 periods of the ABAB partner at 1.9 T would
not be), so a null there kills it. Plus the model-independent Luttinger sum
f₁(n) + f₂(n) = F_L(n) across 53 columns, and the B-window split on the 29.5 T
tone for the F_L-tone-origin discrimination.

**Design (each lever at its floor; one fan, no alternative offered).**
n-window 3.20 → 1.20e12 at D = 0 — top end is the `k_tg` ceiling, and column 0
lands on **exactly** run 6's gate point (Vtg +0.9836, Vbg +1.1661), so the fan
re-measures that spot on a *uniform-1/B* grid against run 6's *uniform-B* one:
the grid-change alias-retirement check for free. B_lo = **0.8 T** (run 6's 22 T
tone onsets at 1.36 T by `sdh_onset`; the 6.9 T tone is censored at the record
edge, so 0.8 T buys the partner ≥5 periods down to n = 2.3e12 and ≥3 down to
1.85e12 — dropping to 0.6 T inflates *both* axes for 1.8 h more). B_hi = 10.0 T
(session cap; the high-B half carries the breakdown test). N_B = 114 uniform in
1/B → Δ(1/B) = 0.0102 /T, Nyquist ceiling 49 T against the fastest expected tone
F_L = 33.1 T (3 samples/period). N_n = 53 → Δn = 0.0385e12 = 2.0 points per LL
ray at B_lo, the n-axis Nyquist floor. δF = 0.87 T.

Sensitivity **inherited from the spot checks at 50 µV** (5 kΩ FS at 10 nA), as
Step 3 requires. Worst corner is low-n × high-B: the measured anchor is run 7 at
|n| = 1.2e12, B = 10 T → 576 Ω = 12% of FS, 8.7× headroom. That leaves the ADC
lightly used, but the electron side is untested at low n in field and clipping is
the unrecoverable failure on a 5 h run — headroom is the right purchase, and the
spot checks' tone SNRs of 20–125 at this same setting show granularity is not the
limiter. `fast_delay = 1.8 s` = 6τ (τ = 0.3 s, 24 dB/oct), the per-column-SdH-FFT
dwell.

**Cost** from this session's own calibration — run 5 (gatemap, 63 × 66,
fast_delay 1.0, slow_delay 3.0) came in at 81.1 min against 74.1 min predicted,
+9.4%. Applying that: 114 × 53 × 1.8 s + 114 × (settle + flyback + slow_delay)
= 3.5 h of grid, + 67 min of rate-limited magnet traverse (0.8 → 10 T at
0.137 T/min), + 6 min to position from 0 T.

**Preconditions the cell asserts (not sets):** thermometry logfile live,
T_sample 1.0–1.5 K, V_si = 0, Keithley nplci = 1, magnet PS heater + output on,
sr1 τ = 0.3 s / 24 dB/oct (fast_delay is derived from it). The gate vectors are
asserted inside the committed validators before any hardware moves.

**Checkpoints.** `hera-watch data --next --follow` is armed as a background
monitor. *First rows* (~2 min in, B ≈ 0.8 T): leakage, railing, a dead or flat
channel, R on the 50–600 Ω scale across the n-line — abort there if wrong, it is
the cheapest kill. *Periodic*: interim per-column FFT once the fan is past
B ≈ 3 T (~2 h), where the heavy tone should already be trackable — continue /
adjust / abandon on that read.

**Endpoint.** Gates park at 0 V in a `finally`. Field is left **deliberately at
10 T**: the investigation's next step (the LK mass split, `temperature-dependence-vti`
Flavor B) rides the magnet back down rather than re-traversing.
