"""SdH spot checks runs 6/7: raw R(B), onset, FFT tones."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

for rid in (6, 7):
    r = open_run(f"data/{rid}")
    chs = resolve_channels(r.meta); cur = current_channel(chs)
    B = r.col('magnet_field') if 'magnet_field' in r.cols else r.col_at(1)
    I = r.col_at(cur.idx) / cur.gain
    v = [c for c in chs if not c.is_current]
    print(f"=== run {rid}: {r.rows} rows, cols {r.cols}")
    print(f"  B {B.min():.3f} -> {B.max():.3f}; I med {np.median(I):.3e} A; voltage chans {[c.cid for c in v]}")
    ch = [c for c in v if c.cid == 'sr1'][0]
    R = np.abs((r.col_at(ch.idx) / ch.gain) / I)
    print(f"  R(sr1): {R.min():.1f} - {R.max():.1f} Ohm; R@Bmin {R[np.argmin(B)]:.1f}, R@Bmax {R[np.argmax(B)]:.1f}")
    o = np.argsort(B); Bs, Rs = B[o], R[o]
    sens = r.meta['measurement_config'].get('sr1_sens')
    fs = (sens / np.median(I)) if sens else None
    print(f"  sr1_sens {sens}, full-scale R ~ {fs:.0f} Ohm" if fs else "  no sens")
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=fs)
        print(on.summary())
    except Exception as e:
        print(f"  sdh_onset FAILED: {type(e).__name__}: {e}")
    m = Bs > 1.0
    f, sp = sdh_fft(Rs[m][:, None], Bs[m])
    s = sp[0]
    k = np.argsort(s)[::-1][:12]
    print(f"  FFT (B>1T, df={1/(1/Bs[m].min()-1/Bs[m].max()):.2f} T): top peaks (T, rel amp):")
    seen=[]
    for i in np.argsort(s)[::-1]:
        if f[i] < 2: continue
        if any(abs(f[i]-x) < 2.0 for x in seen): continue
        seen.append(f[i]); print(f"     F = {f[i]:7.2f} T   amp {s[i]/s.max():.3f}")
        if len(seen) >= 8: break
    np.save(f"hera_scratch/spot{rid}_BR.npy", np.vstack([Bs, Rs]))
