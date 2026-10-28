"""Q2/Q3: clipping, quantization, per-point noise for the live fans (+ QC0426 06-19 run 4)."""
import numpy as np, sys, json, gzip, io
sys.path.insert(0, '.')
from load import load, FANS
from pathlib import Path
QC = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-06-19-QC0426-session-3/data/4')

def lsb(sens):  # SR830 float LSB, empirically 2^(ceil(log2 sens) - 15)
    return 2.0 ** (np.ceil(np.log2(sens)) - 15)

def acf4(s_over_tau):  # normalized autocorrelation of a 4-pole RC filter's output noise at lag s
    t = np.linspace(0, 60, 60001); h = t**3 * np.exp(-t)
    h2 = np.interp(t + s_over_tau, t, h, right=0)
    return (h * h2).sum() / (h * h).sum()

def sigma_d2(x):  # robust per-point sigma from 2nd differences along the last axis
    d2 = x[..., :-2] - 2 * x[..., 1:-1] + x[..., 2:]
    return 1.4826 * np.median(np.abs(d2 - np.median(d2, axis=-1, keepdims=True)), axis=-1) / np.sqrt(6)

def load_qc():
    meta = json.load(open(QC / 'metadata.json')); cols = meta['columns']
    X = np.loadtxt(io.StringIO(gzip.decompress((QC / 'data.tsv.gz').read_bytes()).decode()), delimiter='\t', ndmin=2)
    fs = meta['fast_setpoints']; nfast = len(fs[0]) if isinstance(fs[0], list) else len(fs)
    nrows = X.shape[0] // nfast; X = X[:nrows * nfast]
    g = lambda c: X[:, cols.index(c)].reshape(nrows, nfast)
    lk = {nm: {k: meta['instruments'][nm]['snapshot']['parameters'][k]['value'] for k in ('sensitivity', 'time_constant', 'filter_slope', 'amplitude')} for nm in ('sr0','sr1','sr2','sr3')}
    return dict(name='QC0426-0619-r4', g=g, lk=lk, B=g('magnet_mag')[:, 0], t=g('time'), nrows=nrows, nfast=nfast,
                I=g('sr0_X') / meta['measurement_config']['sr0_gain'], Ibias=2.0 / 1e8)

def main():
    rows_clip = []
    sets = [(load(nm), ['sr1', 'sr0']) for nm in FANS] + [(load_qc(), ['sr1', 'sr2', 'sr3', 'sr0'])]
    for d, chans in sets:
        I = np.median(np.abs(d['I']))
        dt = np.median(np.diff(d['t'], axis=1))
        for ch in chans:
            x = d['g'](ch + '_X'); s = d['lk'][ch]['sensitivity']; tau = d['lk'][ch]['time_constant']
            q = lsb(s)
            on_grid = np.abs(x / q - np.round(x / q)).max()
            a = np.abs(x) / s
            # per-column (fast index) quantization stats over the whole field range
            nlev = np.array([np.unique(x[:, j]).size for j in range(x.shape[1])])
            zero_fast = (np.diff(x, axis=1) == 0).mean(); zero_slow = (np.diff(x, axis=0) == 0).mean()
            row = dict(fan=d['name'], ch=ch, sens_V=s, tau_s=tau, slope=d['lk'][ch]['filter_slope'], I_nA=round(I * 1e9, 2),
                       max_over_fs=round(a.max(), 3), f_ge_095=round((a >= 0.95).mean(), 4), f_ge_100=round((a >= 1.0).mean(), 4),
                       f_ge_105=round((a >= 1.05).mean(), 4), lsb_V=q, off_grid_max=round(on_grid, 3),
                       lsb_ohm=(q / I if ch != 'sr0' else np.nan), zero_dfast=round(zero_fast, 4), zero_dslow=round(zero_slow, 4),
                       levels_per_col_med=int(np.median(nlev)), levels_per_col_min=int(nlev.min()), npts_col=x.shape[0])
            if ch != 'sr0':
                # noise: 2nd differences along fast axis; per row; low-field rows (weakest SdH) and all-row median
                sr = sigma_d2(x)
                B = d['B']; lo = np.argsort(B)[:max(5, len(B) // 10)]
                sig_lo = np.median(sr[lo]); sig_all = np.median(sr)
                rho = acf4(dt / tau)
                # 2nd-diff variance with lag-1 corr rho, lag-2 rho2: var(d2)= sigma^2 (6 - 8 rho + 2 rho2)
                rho2 = acf4(2 * dt / tau); corr = np.sqrt(6 / (6 - 8 * rho + 2 * rho2))
                sig_lo_c = sig_lo * corr
                # expected SR830 input noise 6 nV/rtHz x sqrt(ENBW), ENBW(24 dB) = 5/(64 tau); plus quantization q/sqrt(12)
                enbw = {6: 1/4, 12: 1/8, 18: 3/32, 24: 5/64}[int(d['lk'][ch]['filter_slope'])] / tau
                exp_v = 6e-9 * np.sqrt(enbw); qn = q / np.sqrt(12)
                row.update(dict(dt_fast_s=round(dt, 3), dt_over_tau=round(dt / tau, 2), rho1=round(rho, 3),
                                sigmaV_lowB_nV=round(sig_lo_c * 1e9, 2), sigmaV_allrows_nV=round(sig_all * corr * 1e9, 2),
                                sigmaR_lowB_ohm=round(sig_lo_c / I, 3), en_nV_rtHz=round(sig_lo_c / np.sqrt(enbw) * 1e9, 1),
                                exp_6nV_nV=round(exp_v * 1e9, 2), qnoise_nV=round(qn * 1e9, 2), q_over_sigma=round(q / sig_lo_c, 3),
                                B_lowrows=f"{B[lo].min():.2f}-{B[lo].max():.2f}"))
                # sigma per row vs B for the CSV
                np.savetxt(f"noise_rows_{d['name']}_{ch}.csv", np.c_[B, sr * corr, sr * corr / I], delimiter=',', header='B_T,sigmaV,sigmaR_ohm', comments='')
            rows_clip.append(row)
    import pandas as pd
    df = pd.DataFrame(rows_clip)
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
    print(df.to_string())
    df.to_csv('clip_quant_noise.csv', index=False)

if __name__ == '__main__':
    main()
