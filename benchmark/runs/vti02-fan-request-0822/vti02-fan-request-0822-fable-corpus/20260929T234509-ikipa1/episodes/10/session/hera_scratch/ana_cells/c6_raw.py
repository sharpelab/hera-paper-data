# Run 6 — `sdh-spot-check`, electron side: n = +3.2e12 cm^-2, D = 0; B 0 -> 10 T (50 mT to 1 T, 10 mT above). RAW.
from hera.analysis import resolve_channels, current_channel

def spot_load(fid):
    r = run(fid)
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    i_meas = np.median(r.col(cur.col) / cur.gain)
    v1 = [c for c in ch if c.col.startswith("sr1")][0]
    B, R = r.col("magnet_field"), (r.col(v1.col) / v1.gain) / i_meas
    o = np.argsort(B)
    return r, B[o], R[o], i_meas

r6, B6, R6, I6 = spot_load(6)
print(summarize_run(r6))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.2))
ax[0].plot(B6, R6, lw=0.6)
ax[0].set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)", title=f"run 6 raw: n=+3.2e12, D=0, I={I6*1e9:.2f} nA, sr1 50 uV FS = {50e-6/1.0/I6:.0f} $\\Omega$")
m = B6 >= 1.0   # fine-grid (10 mT) leg only
dR = R6[m] - np.polyval(np.polyfit(B6[m], R6[m], 5), B6[m])
ax[1].plot(1/B6[m], dR, lw=0.6)
ax[1].set(xlabel="1/B (1/T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)", title="background-subtracted (B >= 1 T leg)")
fig.tight_layout(); plt.show()
