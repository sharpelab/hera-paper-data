<!-- variant: open-long | autonomy: HIGH (no method) | length: LONG -->

# Brief

QC0426 (trilayer graphene, VTI fridge, base T ≈ 1.2 K) is characterized at zero
and low field: gate ranges are set (TG on the DC205 / `DC_bias` ∈ [−6.5, 7.5] V,
BG on k_bg ∈ [−5, 4.8] V), a 0 T TG-BG gate map (data/24) fixes the
charge-neutrality line `Vtg ≈ −1.3·Vbg + 0.06`, and a finite-field (B = 3 T) gate
map (data/26) is in hand. The operator has just taken the **first B-n Landau fan
at the charge-neutral D = 0 line** (data/27) by co-sweeping that constant-D
gate-line versus B to 8 T. It shows a sharp insulating charge-neutrality stripe
but only faint, washed-out Landau structure — expected at the VTI's ~1.2 K.

The campaign goal is to map the **Landau-fan / quantum-Hall structure as a function
of carrier density and displacement field** and read off the stacking (ABA vs ABC).
A third gate — a doped-Si global back gate through SiO₂, driven by a second
Keithley (`k_2410`) — is wired and zeroed but not yet used. Given the state above,
**decide and take the next measurement.** The (n, D) convention is the device's own
capacitance-based calc_nD; current is sr0 with explicit gain division
(`I = sr0_X / sr0_gain`), `Rxx = sr{1,2}_X / I`, `sr3` the Hall channel. Choice of
which knob to add next, and of axes / ranges / resolution, is yours.
