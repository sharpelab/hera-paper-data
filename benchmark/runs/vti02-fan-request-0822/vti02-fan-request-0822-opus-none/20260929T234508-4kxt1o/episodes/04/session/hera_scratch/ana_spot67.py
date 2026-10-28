import numpy as np, json
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
NSPOT = {6: +3.2, 7: -1.2}
for k, rid in enumerate([6, 7]):
    r = open_run(f'data/{rid}')
    B = r.col('magnet_field'); t = r.col('time')
    ch = resolve_channels(r.meta); cur = current_channel(ch)
    I = r.col_at(cur.idx)/cur.gain                 # AMPS
    vc = [c for c in ch if not c.is_current][0]
    R = np.abs((r.col_at(vc.idx)/vc.gain)/I)       # OHM
    o = np.argsort(B); Bs, Rs, Is = B[o], R[o], I[o]
    print(f'--- run {rid}: n={NSPOT[rid]:+.1f}e12, rows={r.rows}, T={r.col("T_sample").mean():.3f} K, '
          f'I={np.median(np.abs(Is))*1e9:.2f} nA, R(B~0)={Rs[0]:.1f}, R(10T)={Rs[-1]:.1f} Ohm')
    F_L = luttinger_frequency(abs(NSPOT[rid])*1e16)
    print(f'    Luttinger F (full density, 4-fold) = {F_L:.2f} T')
    fs_ohm = 50e-6/np.median(np.abs(Is))
    print(f'    full scale = {fs_ohm:.0f} Ohm ; max used = {100*Rs.max()/fs_ohm:.1f} % FS')
    # per-point timing model
    dt = np.diff(t[np.argsort(t)]); dB = np.abs(np.diff(np.sort(B)))
    msk = dB > 0
    A = np.vstack([dB[msk], np.ones(msk.sum())]).T
    coef, *_ = np.linalg.lstsq(A, dt[msk], rcond=None)
    print(f'    timing: dt = {coef[0]:.1f} s/T * dB + {coef[1]:.2f} s fixed   (bare ramp would be 438 s/T)')

    axes[0,k].plot(Bs, Rs, lw=0.7); axes[0,k].set_title(f'run {rid}: n={NSPOT[rid]:+.1f}e12, D=0 — raw Rxx')
    axes[0,k].set_xlabel('B (T)'); axes[0,k].set_ylabel('Rxx (Ohm)')

    try:
        so = sdh_onset(Rs, Bs, r_full_scale=fs_ohm)
        print(so.summary())
        out[rid] = dict(n=NSPOT[rid], F_L=float(F_L), onset_b=float(so.onset_b), onset_freq=float(so.onset_freq),
            R0=float(Rs[0]), Rmax=float(Rs.max()), I_nA=float(np.median(np.abs(Is))*1e9),
            tones=[dict(f=float(x.freq), contrast=float(x.contrast), onset=float(x.onset_b),
                        marginal=bool(x.marginal), censored=bool(x.censored), near_res=bool(x.near_residual),
                        harm=(None if x.harmonic_of is None else float(x.harmonic_of))) for x in so.tones])
    except SdhOnsetError as e:
        print(f'    sdh_onset FAILED: {e}'); out[rid]=dict(error=str(e))

    for blo, cc in [(0.8,'C2'), (1.5,'C0'), (3.0,'C1')]:
        m = Bs >= blo
        f, sp = sdh_fft(Rs[m][:,None], Bs[m], nfft=8192, bg_degree=3, log=False)
        s = sp[0]; s = s/s[f>1.0].max()
        axes[1,k].plot(f, s, cc, lw=0.8, label=f'B>{blo} T  (dF={1/(1/blo-1/10):.2f} T)')
        lm = sorted([i for i in range(3,len(s)-3) if s[i]==max(s[i-3:i+4]) and f[i]>1.0], key=lambda i:-s[i])[:6]
        print(f'    FFT B>{blo}: ' + ', '.join(f'{f[i]:.2f}T({s[i]:.2f})' for i in lm))
    axes[1,k].axvline(F_L, color='k', ls='--', lw=1, label=f'F_L={F_L:.1f} T')
    axes[1,k].axvline(F_L/2, color='k', ls=':', lw=1, label=f'F_L/2={F_L/2:.1f} T')
    axes[1,k].set_xlim(0, max(40, F_L*1.4)); axes[1,k].legend(fontsize=7)
    axes[1,k].set_title(f'run {rid} SdH FFT (bg_degree=3)'); axes[1,k].set_xlabel('F (T)')

    m = Bs>=0.8
    p = np.polyfit(Bs[m], Rs[m], 5)
    axes[2,k].plot(1/Bs[m], Rs[m]-np.polyval(p,Bs[m]), lw=0.8)
    axes[2,k].set_xlabel('1/B (1/T)'); axes[2,k].set_ylabel('dRxx (Ohm)'); axes[2,k].set_title(f'run {rid} detrended vs 1/B (B>0.8T)')

plt.tight_layout(); plt.savefig('hera_scratch/spot67.png', dpi=110)
json.dump(out, open('hera_scratch/spot67.json','w'), indent=1)
print('saved hera_scratch/spot67.png')
