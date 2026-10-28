# Run 7, hole n = -1.2e12: F_L = 12.4 T; model: ABAB pair 5.3/7.1 T (the
# near-CNP close-and-balanced exception regime), ABCA 12.4 T (m* ~ 1, LK-dead
# at T_e ~ 8 K). 20 mT grid: tones > ~13 T alias below ~1.3 T; cutoff 0.8 keeps
# the dominant pair Nyquist-clean.
on7 = spot_read(7, 12.4, {"ABAB f1": 5.3, "ABAB f2": 7.1, "ABCA": 12.4}, 0.8,
                "h-side n=-1.2e12")
print(f"\nLuttinger: 4.7 + 6.6 = 11.3 T = {11.3/12.4:.3f} x F_L "
      f"(e-side scale 0.885 — consistent global rescale ~0.89-0.91)")
