# Runs 6-7 (sdh-spot-check) - raw first: every channel, gain-divided, no background removal.
for i in (6, 7):
    g = run(i)
    print(summarize_run(g))
    print("tags:", g.tags, "\n")
    plot_raw(g)
plt.show()
