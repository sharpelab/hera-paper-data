import warnings, numpy as np, json
from hera.analysis import open_run, resolve_channels, sdh_onset
warnings.simplefilter("ignore")
r = open_run("data/6"); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain))
s = B >= 1.0
on = sdh_onset(R[s], B[s], b_lo=1.0, r_full_scale=5000)
for t in on.tones:
    if abs(t.freq - 7.3) < 0.5 or abs(t.freq - 22.3) < 0.6 or abs(t.freq - 29.4) < 0.6:
        bc, snr = np.asarray(t.b_centers), np.asarray(t.snr)
        o = np.argsort(bc)
        print(f"tone {t.freq:.1f} T: " + ", ".join(f"{b:.2f}:{x:.0f}" for b, x in zip(bc[o][:10], snr[o][:10])))
# timing calibration
for rid in (5, 6, 7):
    m = open_run(f"data/{rid}").meta
    print(rid, m.get("function"), "dur", round(m["end_time"] - m["start_time"]), "s", "fast_delay", m.get("fast_delay"), "slow_delay", m.get("slow_delay"), "delay", m.get("delay"))
