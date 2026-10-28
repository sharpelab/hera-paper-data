# Runs 6 & 7 — raw: sdh-spot-check at D = 0 (run-5 cal), sr1 = Rxx (B_1-B_2), I_bias 10 nA
for i in (6, 7):
    g = run(i)
    print(summarize_run(g))
    plot_raw(g)
