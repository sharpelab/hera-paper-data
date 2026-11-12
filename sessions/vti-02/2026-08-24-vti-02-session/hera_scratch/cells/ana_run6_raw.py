# raw view first: every ladder temperature, R_CNP along the CNP line
for _rid in range(6, 13):
    _g = run(_rid)
    print(summarize_run(_g).splitlines()[0], "|",
          f"T = {np.mean(_g.col('T_sample')):.3f} K, {_g.rows} pts")
plot_raw(run(12))     # the hottest one, as the representative raw record
