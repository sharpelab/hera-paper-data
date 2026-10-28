"""Runs 6-7 raw: sdh-spot-check R(B) at D = 0, electron (run 6, n=+3.2e12, 0->10 T) and
hole (run 7, n=-1.2e12, 10->0.3 T ride-down), sr1 50 uV, I ~ 10 nA."""
from hera.analysis import resolve_channels, current_channel

def load_spot(rid):
    r = run(rid)
    B = r.col("magnet_field")
    chs = {c.cid: c for c in resolve_channels(r.meta)}
    cur = current_channel(list(chs.values()))
    I = r.col(cur.col) / cur.gain
    R = (r.col("sr1_X") / chs["sr1"].gain) / I
    srt = np.argsort(B)
    return B[srt], np.abs(R[srt]), np.abs(I[srt]), r

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
for a, (rid, tag) in zip(ax, [(6, "electron n = +3.2e12"), (7, "hole n = -1.2e12")]):
    B, R, I, r = load_spot(rid)
    print(summarize_run(r))
    print(f"run {rid}: R {R.min():.0f}-{R.max():.0f} Ohm, I {I.mean()*1e9:.2f} nA, "
          f"full scale {50e-6/I.mean():.0f} Ohm (max R {100*R.max()*I.mean()/50e-6:.0f}% FS)\n")
    a.plot(B, R, lw=0.6)
    a.set_xlabel("B (T)"); a.set_ylabel("|Rxx| (Ohm)"); a.set_title(f"run {rid} — {tag}, D = 0")
fig.tight_layout()
