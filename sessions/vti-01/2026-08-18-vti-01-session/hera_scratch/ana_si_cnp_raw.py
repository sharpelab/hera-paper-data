# Runs 4-6 — raw first: Si surveys (4: 0->+20, 5: +20->-20) and TG scoping cut (6)
for i in (4, 5, 6):
    g = run(i)
    print(summarize_run(g))
    plot_raw(g)
