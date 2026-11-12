# Run 5 — raw first. Calibration fan, every channel gain-divided on its own axes.
r5 = run(5)
print(summarize_run(r5))
plot_raw(r5)
plt.show()
