## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the stacking discriminator

**Why this, now (plan step 4).** The spot checks (runs 6/7) proved the device
can carry the measurement — SdH onset at or below 0.3 T, peak R ≤ 590 Ω, flat
leakage, T = 1.243 ± 0.032 K — but they **cannot settle the stacking**. On the
electron side (n = +3.2×10¹², F_Onsager = 33.1 T) run 6 shows a 7.1 T tone with
content at 14.1 / 22.2 / 29.5 T, and a single 33.3 T peak dominating the B > 4 T
window. A real second Fermi surface (the ABAB model's heavy band, 25.6 T) and the
3rd harmonic of 7.1 T (21.3 T) are 4.3 T apart — the spot check's frequency
resolution at its usable low edge cannot separate them, and one trace at one
density cannot tell a *band* from a *harmonic* at all. The discriminator is
**F(n): how many SdH branches there are and what fraction of the density each
carries**, tracked across both carrier signs. ABAB → two branches, f₁ + f₂ = 1.
ABCA → one branch at the full Onsager slope h/4e. ABCB → two, strongly e/h
asymmetric. Branch *fractions* are scale-free, so this read survives the fact
that our density scale is still a 9.5 nm geometry prior (only c_bg/c_tg = 0.773
is calibrated from data).

**Design.** B slow (the magnet blocks and is rate-limited — it can only be the
slow axis), (V_tg, V_bg) co-swept fast along region A's D = 0 line. The B grid is
**uniform in 1/B**, which is what `sdh_fft` wants and what makes every column an
even record: 165 rows, Δ(1/B) = 0.0125 T⁻¹ → **F_Nyquist = 39 T** (above the
33.5 T full-density Onsager frequency at the top of the window), with ΔB capped
at 0.25 T so the 4–10 T end keeps 25 rows for a by-eye fan rather than the ~9 a
pure 1/B grid would leave. Frequency resolution is set by the **low** edge, not
the high one: B_lo = 0.5 T gives **df = 0.53 T**, i.e. 21.3 T and 25.6 T are
separated by 8 resolution elements. That is the whole reason the low-B rows are
worth half the run. Fast axis: 101 points, n = −1.26 → +3.235×10¹², Δn =
0.045×10¹² — 5.4 points per filling factor at 10 T, and ≥ 5 mV of margin at both
TG validator ends.

**Two regions, one pair.** Run 5 found **two CNP ridges** — A (slope −0.773) and
B (slope −0.691), offset by n_B ≈ −0.43×10¹² in region-A units — in series on
the only wired Rxx pair (sr1 = B_1–B_2). The fast window straddles both, so this
fan should contain **two fan origins**, at n = 0 and n ≈ −0.43×10¹². Separating
them is how this session delivers the brief's *region-resolved* verdict; if the
two fans differ in branch structure, that is the headline, not a nuisance.

**Preconditions to eyeball before it runs.** T_sample 1.0–1.5 K; B within 50 mT
of 0 (the handoff park); V_si = 0; both gates at 0 V; gate-current NPLC back at
1; PS heater on and output enabled. All printed expected-vs-actual and asserted.
Sensitivity is fixed at **200 µV = 20 kΩ full scale** for the whole map — 34×
the highest R seen so far, sized for the ν = 0 peak at the CNP columns growing
with B (session-notes recipe fix: size to the map's worst corner, not the 1D
peak), not to the ≈ 70–590 Ω away from it.

**Checkpoints (`hera-watch`, armed before launch).** (1) *First rows* — signal
present and not railed at 200 µV, point noise comparable to the ~23 nV of runs
6/7, leakage flat, CNP peak where the run-5 calibration puts it. If the 4× range
step scaled the noise with full scale and killed the low-B contrast, abort there
and re-run at 50 µV; if the CNP columns rail below ~3 T, abort and re-run at
500 µV. (2) *≈ 3 h 25 m in*, at B = 2 T with 120 of 165 rows landed — the 0.5–2 T
block alone gives df ≈ 0.6 T, enough for a first F(n) branch extraction. That is
the go/abandon call: no resolvable fan structure there and the fan is not the
right instrument at this electron temperature, and I fall back to the CNP-vs-D
gap measurement (plan 6a) on the way down. (3) B ≈ 4 T and on completion.

**Coverage trade, stated.** D = 0 only — no finite-D fan this run, which means
the D-induced gap (the secondary ABCA discriminator) stays where run 5 left it;
a second fan at finite D would cost another ~6 h and is deliberately deferred to
after the branch read. The hole side reaches only n = −1.26×10¹², set by the
−0.3 V top-gate limit, against +3.24×10¹² on the electron side, so an e/h
asymmetry read is range-limited on the hole side — worth remembering if the call
comes down to ABCB. Direction: ascending from the park, ending at **10 T** with
the gates returned to 0 V, so the next step (plan 6a, CNP vs D) rides the magnet
back down instead of re-traversing.
