# Runs 0-3 — gate-current-sanity-check, raw view first
for i in range(4):
    g = run(i)
    print(summarize_run(g))
    plot_raw(g)
