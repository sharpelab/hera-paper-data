# Runs 6-7 (`sdh-spot-check`): raw Rxx(B) at fixed (n, D=0), run-5 calibration.
# R = (sr1_X / gain) / I_meas with I_meas from the sr0 transimpedance channel.
from hera.analysis import resolve_channels, current_channel

def spot_trace(rid):
    r = run(rid)
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col(cur.col) / cur.gain
    vch = [c for c in chans if c.cid == "sr1"][0]
    R = (r.col(vch.col) / vch.gain) / I
    B = r.col("magnet_field")
    i = np.argsort(B)
    return B[i], np.abs(R[i]), np.median(np.abs(I))

fig, ax = plt.subplots(1, 2, figsize=(12, 3.6))
for a, (rid, tag) in zip(ax, [(6, "electron n=+3.2e12, B 0->10 T"), (7, "hole n=-1.2e12, B 10->0.3 T")]):
    B, R, Ib = spot_trace(rid)
    a.plot(B, R, lw=0.6)
    a.set_xlabel("B (T)"); a.set_ylabel("Rxx (Ω)")
    a.set_title(f"run {rid} — {tag} (I={Ib*1e9:.1f} nA)")
    print(f"run {rid}: {len(B)} pts, R(B_min)={R[0]:.0f} Ω, R_max={R.max():.0f} Ω, I_bias={Ib*1e9:.2f} nA")
fig.tight_layout()
