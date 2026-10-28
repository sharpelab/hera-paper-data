# Raw view first: both spot checks, gain-divided, no background removal (plot_raw), plus the summaries.
for rid in (6, 7):
    r = run(rid)
    print(summarize_run(r))
    print(f"  T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; I_tg med {np.median(r.col('k_2400_tg_curr'))*1e12:+.0f} pA, "
          f"I_bg med {np.median(r.col('k_2400_bg_curr'))*1e12:+.0f} pA; sr1 X range {r.col('sr1_X').min()*1e6:+.2f}..{r.col('sr1_X').max()*1e6:+.2f} uV of 50 uV FS")
    plot_raw(r); plt.show()
