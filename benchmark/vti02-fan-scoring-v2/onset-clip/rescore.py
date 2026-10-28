"""Rescore the dev set under candidate onset clips. Imports roi/band (unmodified); per-column clip variant of band.cells:
B_lo(n) = max(B_min, clip(n)); column counts when F_light >= 3/window and F_L <= high line (3 rows/period, worst step in window).
Tone cells: sum over adjacent counted columns (sorted by F_light) of dF_light * mean window, + 1 (== band.cells for a flat clip)."""
import sys, json, glob, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); warnings.filterwarnings('ignore')
_argv = sys.argv; sys.argv = [_argv[0], str(Path(__file__).resolve().parents[1])]
import numpy as np, roi, band
sys.argv = _argv
g = roi.g
FITS = json.load(open(Path(__file__).with_name('curve_fits.json')))
S_LIGHT = 2.59                       # median |light Dingle slope| (T), 0825-r8, n >= 1.8
def lin(key): p = FITS[key]; return lambda n: p[1] + p[0] * abs(n)
def sig_eff(I, tau):                 # operational per-point sigma (Ohm): 0825 floor (2.07) + 40 nV/rtHz white, 24 dB
    w = 40e-9 * np.sqrt(5 / (64 * tau)) / (I * 1e-9); return np.hypot(2.07, w)
REF_SIG, REF_DU = sig_eff(49.5, 0.3), (1 - 1 / 8) / 100
def acq_clip(I, tau, du, base='0825-r8:b_ref_op', white=False):
    s = (40e-9 * np.sqrt(5 / (64 * tau)) / (I * 1e-9)) if white else sig_eff(I, tau)
    sr = (40e-9 * np.sqrt(5 / (64 * 0.3)) / 49.5e-9) if white else REF_SIG
    k = (sr / s) * np.sqrt(REF_DU / du)          # SNR relative to the reference fan
    f0 = lin(base)
    return lambda n: 1 / max(1 / f0(n) + np.log(k) / S_LIGHT, 0.05)
def cells_percol(B, ns, clip):
    B = np.unique(B); ok = []
    for x in ns:
        lo = max(B[0], clip(x)); Bw = B[B >= lo - 1e-9]
        if Bw.size < 2: continue
        win = 1 / Bw[0] - 1 / Bw[-1]; hi = 1 / (3 * np.max(-np.diff(1 / Bw))); fl = roi.f_light(x)
        if not np.isnan(fl) and fl >= 3 / win and roi.f_L(x) <= hi: ok.append((fl, win))
    if not ok: return 0, 0.0
    ok.sort(); cells = 1 + sum((b[0] - a[0]) * 0.5 * (a[1] + b[1]) for a, b in zip(ok, ok[1:]))
    return len(ok), cells
def credit_percol(B, ns, clip, at2=0.0):
    B = np.unique(B); tot = 0.0
    for x in ns:
        lo = max(B[0], clip(x)); Bw = B[B >= lo - 1e-9]
        if Bw.size < 2: continue
        win = 1 / Bw[0] - 1 / Bw[-1]; hi = 1 / (3 * np.max(-np.diff(1 / Bw))); fl = roi.f_light(x)
        if np.isnan(fl) or roi.f_L(x) > hi: continue
        p = fl * win; tot += 0.0 if p < 2 else 1.0 if p >= 3 else at2 + (1 - at2) * (p - 2)
    return tot
CLIPS = {
    'own': lambda n: 1e-3,
    '0.45': lambda n: 0.45, '0.55': lambda n: 0.55,
    'mass(model)': lin('0825-r8:a_model'),
    'mass(LK hi)': lin('0825-r8:a_meas_hi'),
    'Dingle ref': lin('0825-r8:b_ref_op'),
    'Dingle ref white': lin('0825-r8:b_ref_white'),
    '1.0': lambda n: 1.0,
}
if __name__ == '__main__':
    latest = {}
    for f in glob.glob('/data/sharpelab/hera-data/frontier/calibration/vti02-live/*/grades/fan-design/*/output.json') + \
             glob.glob('/data/sharpelab/hera-data/replay/runs/vti02-fan-design-*/*/episodes/*/grades/fan-design/*/output.json'):
        ep = f.split('/grades/')[0]
        if ep not in latest or f > latest[ep]: latest[ep] = f
    rows = []
    for ep, f in sorted(latest.items()):
        doc = json.load(open(f))
        if doc.get('status') != 'extracted' or g.tier_of(doc) != 'fan': continue
        case = g.case_of(Path(ep) / 'session'); B = g.field_axis(doc, case); sc = case.get('n_scale', 1.0)
        n = sc * g.columns(doc) / 1e12
        lab = ep.replace('/data/sharpelab/hera-data/', '').replace('frontier/calibration/vti02-live/', 'live ').replace('replay/runs/vti02-fan-design-', '').replace('/episodes/00', '').replace('/episodes/0', ' #')
        li = {x['name']: x for x in doc['lockins']}; tau = li.get('sr1', doc['lockins'][0])['time_constant_s']
        I = doc['excitation_V'] / doc['bias_resistor_ohm'] * 1e9
        Bu = np.unique(B); Bp = Bu[Bu > 0.05]
        low = Bp[Bp <= max(1.2, Bp[min(9, Bp.size - 1)])]
        du = float(np.median(-np.diff(1 / low[::-1]))) if low.size > 1 else REF_DU
        du = abs(du) if du else REF_DU
        clips = dict(CLIPS); clips['Dingle own acq'] = acq_clip(I, tau, du); clips['Dingle own acq (white)'] = acq_clip(I, tau, du, '0825-r8:b_ref_white', white=True)
        res = {k: cells_percol(B, n, c) for k, c in clips.items()}
        cr = {k: credit_percol(B, n, clips[k]) for k in ('0.55', 'Dingle ref', 'Dingle own acq', '1.0')}
        acq_mid = clips['Dingle own acq'](2.5); acq_mid_w = clips['Dingle own acq (white)'](2.5)
        rows.append(dict(lab=lab, B=f"{B.min():.2f}–{B.max():.1f}", I=I, tau=tau, du=du, res=res, cr=cr, acq=acq_mid, acqw=acq_mid_w))
    json.dump(rows, open(Path(__file__).with_name('rescore.json'), 'w'), indent=0, default=float)
    keys = list(rows[0]['res'])
    print('| Episode | Field | I, τ | own-acq clip @n2.5 (op / white) | ' + ' | '.join(keys) + ' |')
    print('|' + '---|' * (4 + len(keys)))
    for r in rows:
        print(f"| {r['lab']} | {r['B']} T | {r['I']:.0f} nA, {r['tau']} s | {r['acq']:.2f} / {r['acqw']:.2f} | " + ' | '.join(f"{r['res'][k][0]} / {r['res'][k][1]:.1f}" for k in keys) + ' |')
    print('\ncredit (2→0):')
    for r in rows: print(r['lab'], {k: round(v, 1) for k, v in r['cr'].items()})
