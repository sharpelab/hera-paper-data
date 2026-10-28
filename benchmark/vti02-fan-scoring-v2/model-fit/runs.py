"""Load every vti-02 SdH-bearing run as a list of density columns (read-only).
Each column: dict(session, run, kind, col, n_frame, B (T, measured if followed), R (ohm), T_K).
n_frame = the session's own calibration frame (linear in the gates), set per session below."""
import gzip, io, json
import numpy as np
from pathlib import Path

NOTES = Path('/home/zack/sharpelab/measurement-env/hera/docs/notes')
E12 = 1.602176634e-19 * 1e16   # C per (1e12 cm^-2)


def nframe(session, vtg, vbg):
    """Session calibration frames (from each run's metadata comments / session_notes)."""
    vtg = np.asarray(vtg, float); vbg = np.asarray(vbg, float)
    ct = 2.7961e-3 / E12   # 1e12 cm^-2 per V, geometry prior c_tg
    if session == '0821':   # run-4 frame: c_bg 2.0330e-3, n_offset -0.069
        return ct * vtg + 2.0330e-3 / E12 * vbg - 0.069
    if session == '0822':   # run-5 cal: ratio 0.773, n_offset -0.089
        return ct * vtg + 0.773 * ct * vbg - 0.089
    if session == '0824':   # D = 0 line V_bg = 1.2737 V_tg, CNP V_tg = -0.003; n(0.5701) = 2.0
        return 2.0 / (0.5701 + 0.003) * (vtg + 0.003)
    if session == '0825':   # LL-ray lever arms, CNP V_tg = +0.0203 at V_bg = 0
        return 1.570 * (vtg - 0.0203) + 1.307 * vbg
    if session == '0823':   # geometry prior c_tg, ratio 0.71 (session), scale 0.82 (run-6 nu fit); CNP V_tg=0.11 at V_bg=0
        return 0.82 * ct * ((vtg - 0.110) + 0.71 * vbg)
    raise KeyError(session)


def _read(session, run):
    d = {'0821': '2026-08-21', '0822': '2026-08-22', '0823': '2026-08-23', '0824': '2026-08-24', '0825': '2026-08-25'}[session]
    p = NOTES / f'{d}-vti-02-session' / 'data' / str(run)
    meta = json.load(open(p / 'metadata.json'))
    raw = (p / 'data.tsv.gz').read_bytes()
    X = np.loadtxt(io.StringIO(gzip.decompress(raw).decode()), delimiter='\t', ndmin=2)
    return meta, X


def _col(meta, X, name, which=-1):
    idx = [i for i, c in enumerate(meta['columns']) if c == name]
    return X[:, idx[which]] if idx else None


def load_run(session, run, kind):
    meta, X = _read(session, run)
    mc = meta['measurement_config']
    I = _col(meta, X, 'sr0_X') / mc['sr0_gain']
    R = _col(meta, X, 'sr1_X') / I
    B = _col(meta, X, 'magnet_field', -1)          # last = measured readback where followed
    T = _col(meta, X, 'T_sample')
    T = T if T is not None else np.full_like(B, np.nan)
    cols = []
    if meta['type'] == '1D':
        vt = _col(meta, X, 'k_2400_tg_volt'); vb = _col(meta, X, 'k_2400_bg_volt')
        if vt is None:   # 08-22 spot checks: gate point from the comment
            txt = ' '.join(meta['comments'])
            import re
            m = re.search(r'\(Vtg, Vbg\) = \(([-+0-9.]+), ([-+0-9.]+)\)', txt)
            vt, vb = float(m.group(1)), float(m.group(2))
        else:
            vt, vb = np.median(vt), np.median(vb)
        o = np.argsort(B)
        cols.append(dict(session=session, run=run, kind=kind, col=0, n_frame=float(nframe(session, vt, vb)),
                         B=B[o], R=R[o], T_K=float(np.nanmedian(T))))
        return cols
    fs = meta['fast_setpoints']; nfast = len(fs[0])
    nrows = X.shape[0] // nfast
    sl = slice(0, nrows * nfast)
    rs = lambda a: a[sl].reshape(nrows, nfast)
    Bg, Rg, Tg = rs(B), rs(R), rs(T)
    vt = rs(_col(meta, X, 'k_2400_tg_volt')); vb = rs(_col(meta, X, 'k_2400_bg_volt'))
    for j in range(nfast):
        b = Bg[:, j]; r = Rg[:, j]; ok = np.isfinite(b) & np.isfinite(r)
        o = np.argsort(b[ok])
        cols.append(dict(session=session, run=run, kind=kind, col=j,
                         n_frame=float(nframe(session, np.median(vt[:, j]), np.median(vb[:, j]))),
                         B=b[ok][o], R=r[ok][o], T_K=float(np.nanmedian(Tg[:, j]))))
    return cols


RUNS = [  # (session, run, kind)
    ('0821', 5, 'spot'), ('0821', 8, 'fan'),
    ('0821', 10, 'lk'), ('0821', 11, 'lk'), ('0821', 12, 'lk'), ('0821', 13, 'lk'), ('0821', 14, 'lk'), ('0821', 15, 'lk'),
    ('0822', 6, 'spot'), ('0822', 7, 'spot'), ('0822', 8, 'fan'),
    ('0822', 9, 'lk'), ('0822', 10, 'lk'), ('0822', 11, 'lk'), ('0822', 12, 'lk'), ('0822', 13, 'lk'), ('0822', 14, 'lk'),
    ('0823', 6, 'fan'), ('0824', 4, 'fan'), ('0824', 5, 'spot'),
    ('0825', 7, 'spot'), ('0825', 8, 'fan'),
]

if __name__ == '__main__':
    for s, r, k in RUNS:
        cs = load_run(s, r, k)
        c0 = cs[0]
        print(s, r, k, 'cols', len(cs), 'n_frame', round(cs[0]['n_frame'], 3), '->', round(cs[-1]['n_frame'], 3),
              'B', round(c0['B'].min(), 3), round(c0['B'].max(), 3), 'pts', len(c0['B']), 'T', round(c0['T_K'], 2),
              'R pct', np.round(np.nanpercentile(c0['R'], [5, 50, 95]), 1))
