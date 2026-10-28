## HERA — buy SNR with drive current, then commit the acquisition config

Corrected scatter (cell 39) at the present 10 nA drive: δR/R = 0.79% at
τ = 0.3 s / 24 dB/oct (2.10 s dwell) and 1.73% at τ = 0.1 s / 24 dB/oct
(0.70 s). Filter slope is not a free parameter — τ = 0.1 s at **12** dB/oct is
7.4× noisier than the same τ at 24 dB/oct, so there is real out-of-band power
sitting near the 13.777 Hz carrier and the steep roll-off is earning its keep.
24 dB/oct stays.

And cell 39 Part 3 taught me what I am actually up against: +50 mV of top gate —
8.7×10¹⁰ cm⁻² on the geometry prior — moved R_xx by 0.36 Ω against a 1.63 Ω
noise floor. Whatever the reason (deep metallic regime far from the CNP, weak
top-gate coupling to the B_1−B_2 segment, or both — Gate C decides), **the
features this campaign needs to resolve are sub-percent of R_xx**. SdH
oscillations downstream will be too. Trading τ down for speed is the wrong
direction; what I want is more signal per unit time.

**Drive current is the lever I have not pulled.** I_bias = 10 nA comes from the
SR830 oscillator at 1.0 V across the 100 MΩ bias resistor, and the oscillator
goes to 5 V. Raising it multiplies V_xx directly, so if the noise is
amplifier- or pickup-dominated the SNR improves proportionally and I can then
afford the short τ *and* be quieter than I am now. If instead the noise is
multiplicative — temperature fluctuation, contact modulation — δR/R will not
budge and the drive buys nothing. **I do not know which, so I measure it rather
than projecting it.**

The ceiling on drive is heating and non-linearity, not the instrument. At
203 Ω the dissipation is trivial (I²R = 5×10⁻¹³ W even at 50 nA), but near the
CNP where R_xx runs to megohms, 50 nA would put tens of mV across the sample —
far above kT/e ≈ 0.1 mV at 1.2 K — which smears exactly the features we care
about. So a high drive is safe *here*, in the metallic regime, and will need
revisiting before any near-CNP or high-resistance work. I will re-check it
there rather than assume today's answer carries.

**This cell:** step the drive 1.0 → 2.0 → 5.0 V (10, 20, 50 nA), re-ranging
both `sr0` and `sr1` at each step from the predicted loading, and read R_xx.
Constant R_xx across a 5× current range **is** the linearity/heating check —
if R_xx drifts with current, the device is heating and the decision rule
rejects that drive. Then, at the chosen drive, re-measure the point-to-point
scatter at both τ = 0.3 and τ = 0.1 (24 dB/oct, dwell-spaced samples as in the
corrected method) and commit.

**Decision rule, stated before the data:** take the largest drive whose R_xx
agrees with the 10 nA value to within 2%; at that drive take τ = 0.1 s if its
measured δR/R comes in under 0.5%, otherwise τ = 0.3 s. Whatever it picks is
printed with the numbers behind it and becomes the session's acquisition
config.

Cost: ~3 minutes. No gate motion, no field motion.
