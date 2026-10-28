## HERA — calibration Landau fan at V_bg = 0 (first field of the session)

`recipe: measurements/landau-fan-vti.md`. **This is a calibration fan, not the
investigation's Step-4 FS-count fan** — its B rows are deliberately far too
coarse for a 1/B FFT. It is here because the zero-field calibration did not
close, and going into field is the way to close it.

**What the gate map (run 4) settled and what it did not.** Settled: the device
has **two resistance features**, and they are not two co-existing doping domains
in the naive sense — ridge B is strong at large +D and dies toward D = 0, while
ridge A is absent below V_bg = −0.29 and strengthens toward large −D (a
second-derivative scan finds no trace of ridge A in any of the 14 rows from
V_bg = −1.30 to −0.36). Also settled: R_xx at the ridge runs from ~2.4 kΩ at
|D| ≈ 0.26 V/nm down to ~230 Ω near D ≈ 0, i.e. the feature gaps strongly with
displacement field.

Not settled — and this is the problem: **ridge B is not a constant-density
contour.** n is linear in both gate voltages, so every constant-n locus is a
straight line in gate space; ridge B's slope changes monotonically from −0.767
to −0.594 across its own track, and a quadratic term cuts the fit residual from
18.1 mV to 3.1 mV. Neither ridge's operating-window slope (−0.576 for B, −0.673
for A) matches the geometry prior of −0.864. So I cannot presently say which
feature is the charge-neutrality point, and every (n, D) coordinate the
FS-count method would quote depends on that answer.

**Why field settles it, and nothing at zero field will.** At fixed B, adjacent
Landau-level minima are separated by **Δn = eB/h** — exactly, from degeneracy
alone, with no band model and no assumed capacitance. Measuring their spacing in
gate voltage therefore gives the lever arm *absolutely*:
c_tg = e²B / (h · ΔV_tg). That is precisely the quantum-Hall lever-arm upgrade
`cnp-and-dline-calibration` Step 5 holds open as the way to promote the scale
from geometry-prior to data-grade, and it simultaneously answers the two things
zero field left ambiguous:

1. **Which feature is the CNP** — the CNP is the ν = 0 state, the one the LL
   fan radiates *from*. A feature that is not a charge-neutrality point does not
   emit a Landau fan.
2. **One region or two** — two domains at different densities would produce
   **two superposed fans with different origins**, which is unmistakable. This
   is the direct test of the confound Gate C raised, and the reason it matters
   is unchanged: two SdH tones from two doping domains would masquerade as the
   two Fermi surfaces that are exactly the ABAB signature this campaign is
   trying to detect.

**Design.** V_bg = 0 is chosen because **both ridges sit inside the top-gate
window there** (B at V_tg = +0.113, A at −0.203), so a single fast sweep crosses
both and any second fan origin is caught in the same rows. B slow over
0 → 6 T in 0.5 T steps (13 rows); V_tg fast over the full committed window in
201 points (6.5 mV). At 6 T one filling factor spans ΔV_tg ≈ 83 mV ≈ 13 fast-axis
points on the geometry prior — comfortably resolvable, and the *measured*
spacing is the output, so a wrong prior only changes how many points I get, not
the answer.

**Cost, and why the fan shape is affordable.** B is the **slow** axis, so the
magnet ramps once per row rather than once per point — the VTI variant's key
cost fact, and the reason a fan is cheap here while a fine 1D field sweep is
not (a blocking per-point settle would dominate). Traverse 6 T / 0.137 T·min⁻¹
≈ 44 min, grid 13 × 201 × 0.87 s ≈ 38 min. **ETA 1h40m** with margin.

**Coverage trade, stated.** V_bg is pinned at 0, so D varies along the fast axis
(−0.047 to +0.157 V/nm) rather than being held. That is acceptable *for this
purpose* — the LL spacing that sets the lever arm is a degeneracy statement and
does not care about D — but it means this fan does **not** deliver the
investigation's D ≈ 0 requirement and must not be read as an FS-count fan. A
second short fan with V_tg fixed and V_bg fast would give c_bg the same way; I
expect to need it, and it is cheap once the magnet is already at field.

**`sr1` stays at 500 µV** (≈10 kΩ ceiling). The CNP may well rail at high field
where the ν = 0 state gets strongly insulating — that is an accepted trade,
because the lever arm is read from LL minima on the *metallic flanks*, where a
tighter range keeps resolution. `hera-watch` reports the load per row, so railing
will be visible rather than silent.

**Field endpoint:** the sweep ends at 6 T and I leave it there — never
re-traverse without a reason (rig card). The next step decides where the magnet
goes, and riding it home as a measured ramp is the natural SdH spot check.

**Checkpoints:** first rows for railing/leakage and a per-point re-price; then
per-row as the fan builds, with LL structure expected to emerge above ~2 T.
