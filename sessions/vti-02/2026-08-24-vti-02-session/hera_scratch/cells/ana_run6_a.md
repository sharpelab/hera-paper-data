## Runs 6–12 — `tladder-cnp`: the activation gap Δ(D)

**Why / what we're testing:** everything up to here says "the resistance at neutrality rises
10× with displacement field." This says what that rise *is*, in meV, and — critically — it is
the one measurement immune to the unknown Hall-bar geometry, because activation is a ratio.

The specific worry it addresses: run 3's R_CNP(D) **saturates** above D/ε₀ ≈ 0.23 V/nm
instead of continuing up exponentially, which is what a parallel conduction path or
disorder-induced in-gap states look like. If such a floor dominated the transport, "R rose
10×" would be a much weaker statement than it appears.

Seven temperatures — base, 8, 12, 17, 23, 30, 40 K via `set_both(T, ratio=0.95)` — each with
a 245-point co-swept sweep walking the measured CNP line five times at perpendicular V_bg
offsets, so R_CNP is taken as the maximum over offsets and cannot be spoofed by the line
drifting or the CNP moving as the sample warms. Every setpoint settled to within 0.01 K
(σ ≈ 0.002 K) in ~140 s. Fits use T ≥ 8 K only: the rig's electron temperature is ~8 K, and
the data show it — R_CNP is flat between 1.2 and 8 K.
