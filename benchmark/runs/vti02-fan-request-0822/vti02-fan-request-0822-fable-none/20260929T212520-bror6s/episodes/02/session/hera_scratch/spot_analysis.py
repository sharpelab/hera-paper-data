# SdH spot checks: run 6 (electron n=+3.2e12, B 0->10 T) and run 7 (hole n=-1.2e12, B 10->0.3 T)
# Raw R(B), then sdh_onset tone table + FFT. Numbers for the fan design.
import numpy as np, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

BASE = '/home/hera/measurements/zack/20260822-vti-02/data'

def load(rid):
    r = open_run(f'{BASE}/{rid}')
    print(f'--- run {rid} ---')
    print(summarize_run(r))
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    v = [c for c in chans if not c.is_current]
    assert len(v) == 1, v
    B = r.col('magnet_field')
    I = r.col_at(cur.idx) / cur.gain if abs(cur.gain) != 1 else r.col_at(cur.idx)
    # fp already gain-divides? -> fp(sr0.X) was followed with gain=1, so divide here by mc gain
    mc = r.meta['measurement_config']
    g0 = mc['sr0_gain']; g1 = mc.get('sr1_gain', 1.0) or 1.0
    I = r.col('sr0_X') / g0
    V = r.col('sr1_X') / g1
    R = V / I
    return r, B, R, I, V

for rid in (6, 7):
    r, B, R, I, V = load(rid)
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    print(f'R(B~min)={R[:5].mean():.1f} Ohm, R(B~max)={R[-5:].mean():.1f} Ohm, I median={np.median(np.abs(I))*1e9:.3f} nA')
    rfs = 50e-6 / np.median(np.abs(I))  # sensitivity / I_bias
    try:
        so = sdh_onset(np.abs(R), B, r_full_scale=rfs)
        print(so.summary())
    except SdhOnsetError as e:
        so = None
        print(f'sdh_onset FAILED: {e}')
    # FFT over the field windows
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].plot(B, np.abs(R), lw=0.6); ax[0].set_xlabel('B (T)'); ax[0].set_ylabel('|Rxx| (Ohm)')
    ax[0].set_title(f'run {rid} raw')
    m = B >= 1.0
    ax[1].plot(1/B[m], np.abs(R)[m], lw=0.6); ax[1].set_xlabel('1/B (1/T)'); ax[1].set_title('vs 1/B (B>1T)')
    for blo in (1.5, 2.5, 4.0):
        try:
            f, sp = sdh_fft(np.abs(R)[:, None], B, b_range=(blo, B.max()), nfft=4096, log=False)
            ax[2].plot(f, sp[0] / sp[0].max(), lw=0.8, label=f'B>{blo}T')
        except Exception as e:
            print(f'fft b_lo={blo}: {e}')
    ax[2].set_xlim(0, 60); ax[2].set_xlabel('F (T)'); ax[2].legend(); ax[2].set_title('FFT in 1/B (norm.)')
    fig.tight_layout()
    fig.savefig(f'/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{rid}.png', dpi=110)
    print()
