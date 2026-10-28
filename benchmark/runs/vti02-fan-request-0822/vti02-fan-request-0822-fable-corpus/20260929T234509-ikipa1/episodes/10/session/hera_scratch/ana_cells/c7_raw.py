# Run 7 — `sdh-spot-check`, hole side: n = -1.2e12 cm^-2, D = 0; B 10 -> 0.3 T (20 mT, magnet ride-down). RAW.
r7, B7, R7, I7 = spot_load(7)
print(summarize_run(r7))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.2))
ax[0].plot(B7, R7, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)", title=f"run 7 raw: n=-1.2e12, D=0, I={I7*1e9:.2f} nA")
m = B7 >= 0.71
dR = R7[m] - np.polyval(np.polyfit(B7[m], R7[m], 5), B7[m])
ax[1].plot(1/B7[m], dR, lw=0.6)
ax[1].set(xlabel="1/B (1/T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)", title="background-subtracted (B >= 0.71 T = onset)")
fig.tight_layout(); plt.show()
