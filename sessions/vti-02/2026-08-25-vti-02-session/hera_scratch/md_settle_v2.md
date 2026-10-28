## HERA — settling/noise, corrected (my cell 37 Part 2 was biased)

**`sr1` is ranged** (cell 37 Part 1): 5 µV full scale, |X|/sens = 0.40,
**R_xx(0, 0) = 203.2 Ω**, θ = −3.4°. Clean resistive four-terminal signal on
B_1−B_2 — the provided contact configuration is live. That 203 Ω is the
metallic value; sensitivity gets revisited once the CNP peak height is known.

**Part 2 of cell 37 is not trustworthy and I am re-running it.** It sampled
`sr1.X` 24 times back-to-back — about 0.7 s of wall clock total. At τ = 0.3 s
the lock-in output is smoothed over 0.3 s, so those 24 samples contain roughly
two independent values, and the reported std is small because the samples are
correlated, not because the channel is quiet. The bias runs one way: it
flatters large τ and penalises small τ, which is exactly the comparison the
cell existed to make. The 0.06%-vs-4.46% cliff it printed is an artifact of the
sampling, not a measurement, and I am not pricing the session off it.

The corrected test samples **at the dwell interval** (7τ at 24 dB/oct, 5τ at
12 dB/oct) — the spacing consecutive points actually have inside a sweep — so
what comes out is the point-to-point scatter a real sweep would see. Same four
candidates, 24 samples each, which costs ~50 s for the τ = 0.3 s case and less
for the rest.

**Part 3 is new and is the measurement I should have made first**: step V_tg by
+50 mV and sample `sr1.X` every 100 ms for 6 s, then step back. That measures
*in situ* settling — Keithley ramp at `volt.step` = 5 mV, plus device response,
plus lock-in filter — rather than trusting k·τ theory. The dwell I commit comes
from where that trace plateaus, and it also tells me whether the gate itself
contributes settling I have been ignoring. The step is 50 mV inside TG
[−0.3, +1.0] and returns to 0; both gate currents are read before and after.

Why this matters enough to spend four minutes on: everything downstream is
priced off the per-point dwell. At 2.35 s/pt a 101×101 first gate map is 6.7 h;
at 0.95 s/pt it is 2.7 h. That factor decides whether the first map is an
afternoon or most of the session's magnet-free time, and it propagates into
every fan and temperature ladder after it. It is worth measuring properly once.

Cost: ~4 minutes. No field motion; one 50 mV gate excursion that returns to 0.
