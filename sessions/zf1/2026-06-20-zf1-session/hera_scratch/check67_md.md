## HERA — verify rotator-servo lock-ins sr830_6 (θ) / sr830_7 (φ) excitations are off

Read-only. The rotator (ANC350 θ/φ) is blocklisted this session, so sr830_6/7 sine outputs should be at the SR830 minimum (≈4 mV) — effectively off — so they don't inject into the transport noise floor (θ/φ sin-out off is the documented noise-reduction step on this rig). **Run this before the effective-zero field sweep**; if either reads a large amplitude, we turn it down first (cleaner floor for the fragile-SC dip search). No writes.
