## Runs 6, 7 — SdH spot checks (`sdh-spot-check`), D = 0, both carrier signs

Step 3 of `investigations/tetralayer-stacking-fs-count`: which tones are present, which
side is cleaner, and the measured onset / sampling / sensitivity to hand to the Step-4 fan.
Raw trace first, then `hera.analysis.sdh_onset` (computed, not eyeballed), then the 1/B FFT
with the mandatory low-B / high-B window split.

- **run 6** — electron, nominal n = +3.20e12 cm⁻², (V_tg, V_bg) = (+0.9836, +1.1661), B 0 → 10 T
- **run 7** — hole, nominal n = −1.20e12 cm⁻², (V_tg, V_bg) = (−0.2770, −0.4650), B 10 → 0.3 T

`R_xx = (sr1_X / 1) / I` with `I = sr0_X / (−1e6)` — the measured drain current, per the
device card's channel table. Frequencies are read against `F_L = (h/4e)·|n|` on the run-5
nominal calibration; the **global density rescale** is pinned on the whole peak set below,
never per tone.
