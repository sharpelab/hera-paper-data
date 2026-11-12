# Gate C — raw first. Four gate-current-sanity-check legs, every lock-in
# channel gain-divided on the run's own axes. Rails, dead channels, and drift
# are visible here and hidden by any derived view.
for rid in (0, 1, 2, 3):
    r = run(rid)
    print(summarize_run(r))
    plot_raw(r)
    plt.show()
