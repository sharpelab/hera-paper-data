## Run 5 — `sdh-downsweep`: the definitive Fermi-pocket count

**Why / what we're testing:** the activation ladder needs zero field, so the 6 T → 0 ramp
was unavoidable. Measuring through it cost ~13 min over a bare ramp and bought 100 field
points (6 → 0.5 T, uniform in 1/B) at 5 fixed densities on the D = 0 line. The point is
resolution: this record gives **0.55 T** resolution with Nyquist **27.6 T**, against the
fan's 0.87 T and 17.3 T — the fan aliased its top densities, this does not.

**The test needs no calibration.** Two Fermi pockets produce two SdH tones, *both*
proportional to n, whose frequencies sum to the full Onsager value. One pocket produces a
single tone carrying all of it. Counting tones that scale with density is independent of the
absolute density scale — which matters here, because that scale is exactly what this session
cannot pin down independently (no Hall pair is wired).
