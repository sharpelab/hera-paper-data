**Read:** the device is alive and well behaved, and the CNP sits at **V_bg ≈ −0.20 V** at
V_tg = 0 — a clean, symmetric dip in the drain current. Leakage is clean: both gate
currents are flat and voltage-independent (TG −100 pA, BG +25 pA offsets on a 1.05 µA
range at NPLC 1, i.e. offset and read noise, not leakage). The ~100 pA spikes appear
**simultaneously on both independent Keithleys**, so they are pickup or a read collision —
real gate leakage cannot be common-mode across two separate instruments.

Two things this run taught that changed the plan:

1. **`sr1` clipped over 30 % of the sweep** (2 µV full scale, pinned above 218 Ω), so the
   CNP peak height is unmeasured here. Run 1 repeats the cut re-ranged.

2. **The drain current cannot substitute for Rxx.** I had planned to read the CNP off
   `sr0`, but with a 100 MΩ bias resistor defining the current, dI/I = −dR₂ₜ/10⁸: a
   channel going 100 Ω → 100 kΩ moves the current by 0.1 %. The dip *is* visible (0.7 %),
   but that corresponds to ~0.7 MΩ of R₂ₜ change, which — against a four-terminal Rxx of
   ~100 Ω — means it is the **contacts**, not the channel, doing the moving (~0.4 MΩ per
   contact, roughly doubling through the CNP). Under a high-impedance current bias the
   drain current is a contact-resistance probe, not a channel probe.
