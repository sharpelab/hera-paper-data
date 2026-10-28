# Runs 6-7 raw: |Rxx|(B) at the two D = 0 spots (measured-current R, gain-divided)
from hera.analysis import resolve_channels, current_channel, sdh_onset, SdhOnsetError

def spot_trace(rid):
    r = run(rid)
    print(summarize_run(r), "\n")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col(cur.col) / cur.gain
    v = [c for c in chans if not c.is_current and c.cid == "sr1"][0]
    B, R = r.col("magnet_field"), (r.col(v.col) / v.gain) / I
    i = np.argsort(B)
    return B[i], np.abs(R[i]), I

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
spots = {}
for a, (rid, lab) in zip(ax, [(6, "run 6 — electron n = +3.2e12"), (7, "run 7 — hole n = -1.2e12")]):
    B, R, I = spot_trace(rid)
    spots[rid] = (B, R, I)
    a.plot(B, R, lw=0.5)
    a.set_xlabel("B (T)"); a.set_ylabel("|Rxx| (Ω)"); a.set_title(lab)
fig.suptitle("Runs 6–7 — SdH spot checks, D = 0 (run-5 cal), T ≈ 1.2–1.3 K")
plt.tight_layout(); plt.show()
