## HERA — P1b: re-range sr1, re-run the back-gate cut

Plan step **P1** (second pass). Run 0 passed Gate C but clipped the one channel that
matters. This cell fixes the acquisition and repeats the cut; it costs ~2.5 min and
gates the ~45 min map that follows, so it runs first.

**What run 0 established.** The drain current traces a clean, symmetric dip centred at
**V_bg = −0.200 V** at V_tg = 0 — that is the CNP, and on the geometry prior it puts the
intrinsic doping at n_offset ≈ +3.0 × 10¹¹ cm⁻² (slightly electron-doped) with the CNP
sitting at D/ε₀ ≈ +0.027 V/nm, i.e. essentially zero field. Leakage is clean: both gate
currents are flat and voltage-independent (TG −100 pA, BG +25 pA offsets), and the ~100 pA
spikes appear **simultaneously on both independent gates**, which is pickup or a read
collision, not leakage — real gate leakage cannot be common-mode across two separate
Keithleys.

**Why sr1 must be re-ranged.** Rxx clipped at 218 Ω (fs 1.09) over 30 % of the sweep,
so the CNP peak height is unmeasured. The drain current cannot substitute: the 100 MΩ
bias resistor defines the current, so a device going 100 Ω → 100 kΩ moves I by ~0.1 %.
New sensitivity **1 mV** = 100 kΩ of Rxx headroom at 10 nA bias, which covers a flat-band
CNP; the metallic end (65 Ω, 0.65 µV) sits 60 dB down, well inside an SR830's reserve.

**Why τ drops to 0.1 s.** Compliant dwell is 7τ, so 0.3 s costs 2.1 s/pt and prices the
coarse map at ~1.9 h; 0.1 s costs 0.7 s/pt and prices it at ~45 min. At the 13.777 Hz
drive a 100 ms 24 dB/oct filter still puts 2f (27.6 Hz) about 99 dB down. It is set on
**sr0 as well as sr1** — the dwell is gated by the slowest channel, so re-ranging only
sr1 would buy nothing. Both are instrument-configuration writes on lock-in inputs; no
validator, gate limit, field cap or T cap is touched.

**One systematic this run will let me size.** R₂ₜ off-CNP is ~0.75 MΩ against a
four-terminal Rxx of ~100 Ω, so the **contacts dominate the two-terminal resistance**
(~0.4 MΩ each), and they roughly double through the CNP. That matters because the SR830
input is 10 MΩ: ~0.8 MΩ of series probe resistance divides Vxx down by ~7 %, and worse
if the probe contacts go strongly resistive at the CNP. So absolute Rxx carries a
systematic that grows near the CNP. `sr1_Y` (the quadrature) is followed and plotted
precisely so I can watch for the phase drift that would flag it.

**Reverse direction** (+2.00 → −1.30 V): starts where run 0 left the gate, and buys a
hysteresis check against run 0 for free.

**Checkpoint:** first digest rows for clipping and for the new noise floor at the
metallic end — if 1 mV proves too coarse there, that shows up immediately and costs
2 min, not 45.
