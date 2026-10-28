"""Runs 6-7 raw: sdh-spot-check Rxx(B) at D = 0 (run-5 cal): run 6 electron n = +3.2e12 (B 0 -> 10 T),
run 7 hole n = -1.2e12 (10 -> 0.3 T ride-down). sr1 50 uV, I = 10 nA; R from measured drain current."""
from hera.analysis import resolve_channels, current_channel


def spot_trace(rid):
    r = run(rid)
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    I = r.col(cur.col) / cur.gain
    v = [c for c in chs if not c.is_current and np.abs(r.col(c.col)).max() > 0][0]
    R = (r.col(v.col) / v.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    return B[o], np.abs(R[o])


fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, (rid, lab) in zip(ax, ((6, "n = +3.2e12 (electron)"), (7, "n = -1.2e12 (hole)"))):
    B, R = spot_trace(rid)
    print(f"run {rid}: {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, |Rxx| {R.min():.0f}-{R.max():.0f} Ohm")
    a.plot(B, R, lw=0.6)
    a.set(xlabel="B (T)", ylabel="|Rxx| (Ohm)", title=f"run {rid} — {lab}, D = 0")
fig.tight_layout()
plt.show()
