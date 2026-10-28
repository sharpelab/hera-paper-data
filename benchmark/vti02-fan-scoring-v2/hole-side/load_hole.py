"""Every vti-02 hole-side R(B) trace at (or near) D = 0, one monotone trace per density (read-only).

Trace dict: id, session, run, col, n_frame (session frame, 1e12 cm^-2), n_scale (grader, electron-side),
B (T, measured readback, ascending), R (ohm), I_nA, tau_s, sens_V, T_K, grid, note."""
import gzip, io, json
from pathlib import Path
import numpy as np

NOTES = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes')
E12 = 1.602176634e-19 * 1e16
CT = 2.7961e-3 / E12                      # geometry-prior c_tg, 1e12 cm^-2 per V
N_SCALE = {'0821': 0.92, '0822': 0.886, '0823': 0.90, '0824': 0.90, '0825': 0.95}


def nframe(session, vtg, vbg):
    """The session's own density frame (as its notebooks / grader extractor use it)."""
    vtg = np.asarray(vtg, float); vbg = np.asarray(vbg, float)
    if session == '0822':   # run-5 cal: ratio 0.773, n_offset -0.089
        return CT * vtg + 0.773 * CT * vbg - 0.089
    if session == '0824':   # D = 0 line V_bg = 1.2737 V_tg, CNP V_tg = -0.003; n(0.5701) = 2.0
        return 2.0 / (0.5701 + 0.003) * (vtg + 0.003)
    if session == '0825':   # LL-ray lever arms, CNP V_tg = +0.0203 at V_bg = 0
        return 1.570 * (vtg - 0.0203) + 1.307 * vbg
    if session == '0823':   # geometry prior c_tg, ratio 0.71, CNP V_tg = 0.11 at V_bg = 0 (no 0.82 fan scale)
        return CT * ((vtg - 0.110) + 0.71 * vbg)
    raise KeyError(session)


def read(session, run):
    d = f'2026-08-{session[2:]}-vti-02-session'
    p = NOTES / d / 'data' / str(run)
    meta = json.load(open(p / 'metadata.json'))
    X = np.loadtxt(io.StringIO(gzip.decompress((p / 'data.tsv.gz').read_bytes()).decode()), delimiter='\t', ndmin=2)
    return meta, X


def col(meta, X, name, which=-1):
    idx = [i for i, c in enumerate(meta['columns']) if c == name]
    return X[:, idx[which]] if idx else None


def lockins(meta):
    out = {}
    for nm in ('sr0', 'sr1'):
        pp = meta['instruments'][nm]['snapshot']['parameters']
        out[nm] = {k: pp[k]['value'] for k in ('sensitivity', 'time_constant', 'filter_slope', 'amplitude') if k in pp}
    return out


def _base(session, run, meta, X):
    mc = meta['measurement_config']
    I = col(meta, X, 'sr0_X') / mc['sr0_gain']
    R = col(meta, X, 'sr1_X') / I
    B = col(meta, X, 'magnet_field', -1)
    T = col(meta, X, 'T_sample')
    lk = lockins(meta)
    return I, R, B, T, lk


def mk(session, run, colidx, n_frame, B, R, I, T, lk, grid, note, t=None):
    o = np.argsort(B)
    ok = np.isfinite(B[o]) & np.isfinite(R[o])
    return dict(id=f'{session}-r{run}' + (f'-c{colidx}' if colidx is not None else ''), session=session, run=run, col=colidx,
                n_frame=float(n_frame), n_scale=N_SCALE[session], n_act_e=float(n_frame) * N_SCALE[session],
                B=B[o][ok], R=R[o][ok], I_nA=float(np.nanmedian(np.abs(I)) * 1e9), tau_s=lk['sr1']['time_constant'],
                sens_V=lk['sr1']['sensitivity'], T_K=float(np.nanmedian(T)) if T is not None else np.nan, grid=grid, note=note)


def load_all(include_ramp=True, n_max=-0.05):
    out = []
    # 08-22 r7: 1D spot, gate point from the comment
    meta, X = read('0822', 7)
    I, R, B, T, lk = _base('0822', 7, meta, X)
    out.append(mk('0822', 7, None, nframe('0822', -0.2770, -0.4650), B, R, I, T, lk, 'uniform-B 20 mT, 10 -> 0.3 T', '1D spot check'))
    # 08-24 r4 (fan, 46 cols) and r5 (5 densities, col 0 = hole); 08-25 r7 (5 densities, col 0 = hole)
    for s, r, note in (('0824', 4, '1/B fan 0.75-6 T, 40 rows'), ('0824', 5, 'multi-density 1/B, 6 -> 0.5 T, 100 rows'),
                       ('0825', 7, 'multi-density uniform-B 1.5-6 T, 187 rows')):
        meta, X = read(s, r)
        I, R, B, T, lk = _base(s, r, meta, X)
        nf = len(meta['fast_setpoints'][0])
        nr = X.shape[0] // nf
        rs = lambda a: a[:nr * nf].reshape(nr, nf)
        vt, vb = rs(col(meta, X, 'k_2400_tg_volt')), rs(col(meta, X, 'k_2400_bg_volt'))
        Ig, Rg, Bg, Tg = rs(I), rs(R), rs(B), rs(T)
        for j in range(nf):
            n = float(nframe(s, np.median(vt[:, j]), np.median(vb[:, j])))
            if n > n_max:
                continue
            out.append(mk(s, r, j, n, Bg[:, j], Rg[:, j], Ig[:, j], Tg[:, j], lk, note, 'fan column' if r == 4 else 'split from multi-density sweep'))
    if include_ramp:   # 08-23 r6: measure-while-ramping D ~ 0 fan, 0.6 -> 8 T, 38 rows (B read per point)
        meta, X = read('0823', 6)
        I, R, B, T, lk = _base('0823', 6, meta, X)
        nf = len(meta['fast_setpoints'][0])
        nr = X.shape[0] // nf
        rs = lambda a: a[:nr * nf].reshape(nr, nf)
        vt, vb = rs(col(meta, X, 'k_2400_tg_volt')), rs(col(meta, X, 'k_2400_bg_volt'))
        Ig, Rg, Bg, Tg = rs(I), rs(R), rs(B), rs(T)
        for j in range(nf):
            n = float(nframe('0823', np.median(vt[:, j]), np.median(vb[:, j])))
            if n > n_max:
                continue
            out.append(mk('0823', 6, j, n, Bg[:, j], Rg[:, j], Ig[:, j], Tg[:, j], lk, 'continuous ramp 0.6-8 T, 38 rows', 'ramp fan column'))
    return out


if __name__ == '__main__':
    for t in load_all():
        B = t['B']
        print(f"{t['id']:14s} n_frame {t['n_frame']:+.3f} n_e {t['n_act_e']:+.3f} B {B.min():.2f}-{B.max():.2f} pts {B.size} "
              f"I {t['I_nA']:.1f} nA tau {t['tau_s']} sens {t['sens_V']} T {t['T_K']:.2f} R {np.percentile(t['R'], [5, 50, 95]).round(0)}")
