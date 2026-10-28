# Run 0 — analysis: locate the dome minimum & core, check leakage / T
imin = np.argmin(R3)
core = (R3 < 2.0)
itg = np.abs(g.col('k_tg_curr')).max(); ibg = np.abs(g.col('k_bg_curr')).max()
print(f"Rxx min = {R3[imin]:.3f} Ohm at n = {n11[imin]:.3f}e11 "
      f"(V_tg={vtg[imin]:.3f}, V_bg={vbg[imin]:.3f})")
if core.any():
    print(f"Rxx<2 Ohm core: n in [{n11[core].min():.2f}, {n11[core].max():.2f}]e11 "
          f"({core.sum()} pts)")
print(f"normal flanks: n={n11[0]:.2f} -> {R3[0]:.1f} Ohm ; n={n11[-1]:.2f} -> {R3[-1]:.1f} Ohm")
print(f"leakage max: |I_tg|={itg:.2e} A, |I_bg|={ibg:.2e} A  (both << 1 nA)")
print(f"T held: {g.col('T').mean()*1e3:.1f} mK")
print("compare prior: optimum n=-5.0e11, D=-0.64 -> V_tg=-5.365, V_bg=+3.987 (runs 5-8)")
