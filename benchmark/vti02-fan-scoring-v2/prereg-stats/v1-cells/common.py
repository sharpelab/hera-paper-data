"""Episode inventory and the generalized band scorer for the pre-registration study.

Read-only over $HERA_DATA. Imports roi.py / band.py (never edits them); `score()` at the
default knobs reproduces band.cells / band.credit (checked by `selftest()`).
"""
import csv, glob, json, os, sys, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings('ignore')
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
sys.path.insert(0, str(TOP))
_argv, sys.argv = sys.argv, [sys.argv[0], str(TOP)]  # band.py reads its import path from argv[1]
import roi, band  # noqa: E402
sys.argv = _argv
g = roi.g
RUNS = Path('/data/sharpelab/hera-data/replay/runs')
LIVE = Path('/data/sharpelab/hera-data/frontier/calibration/vti02-live')
OUT = TOP / 'prereg-stats'

CUT_0822 = '3a4cf818'  # the vti02-fan-design frontier of record
CUT_0821 = '45433bea'  # the earlier 08-21 cut the case used on 2026-09-22
MODEL_SHORT = {'claude-fable-5': 'fable', 'claude-opus-5': 'opus', 'gpt-5.6-sol': 'sol', 'gpt-6-astra': 'astra',
               'claude-sonnet-5': 'sonnet', 'claude-haiku-4-5-20251001': 'haiku', 'gpt-5.6-luna': 'luna'}
MATRIX_MODELS = ('fable', 'opus', 'sol', 'astra')

# ---------------------------------------------------------------- hand extractions
# Four episodes at the 08-22 cut landed a fan but were never graded. Extracted by hand from
# appended_cells.json (calibration frame; tau/amplitude inherited from the state: sr1 tau 0.3 s,
# 1 V / 100 MOhm). Dev-set only; flagged `hand` everywhere.
# Every dev design ran both 2400 gate-current reads at NPLC 1, inherited from the 08-22 state
# (nplc-smoke/); extractions from before the grader recorded NPLC get this.
NPLC1_READS = [{'name': g, 'nplc': 1.0, 'nplc_set_in_answer': False} for g in ('k_2400_tg_curr', 'k_2400_bg_curr')]


def _doc(B, n0, n1, ncol, slow, fast, sens):
    return {'status': 'extracted', 'landed': 'fan', 'form': '2d_megasweep', 'field_mode': 'invB',
            'B_values': list(map(float, B)), 'B_min_T': float(min(B)), 'B_max_T': float(max(B)), 'n_B': len(B),
            'spacing': 'custom', 'n_min_cm2': min(n0, n1) * 1e12, 'n_max_cm2': max(n0, n1) * 1e12,
            'n_columns': ncol, 'D': 0.0, 'slow_axis': 'B', 'slow_delay_s': slow, 'fast_delay_s': fast,
            'lockins': [{'name': 'sr1', 'sensitivity_V': sens, 'sensitivity_set_in_answer': True,
                         'time_constant_s': 0.3, 'time_constant_set_in_answer': False}],
            'gate_current_reads': NPLC1_READS, 'excitation_V': 1.0, 'bias_resistor_ohm': 1e8, 'n_fans': 1,
            'stated_wall_clock_h': None, 'notes': 'hand-extracted from appended_cells.json',
            'flags': [{'kind': 'hand', 'severity': 'info', 'note': 'hand extraction, dev set only'}]}


def _load(path):
    """A stored extraction, as the current grader reads it."""
    doc = json.load(open(path))
    if doc.get('status') == 'extracted' and 'lockins' in doc:
        doc.setdefault('gate_current_reads', NPLC1_READS)
    return doc

HAND = {
    'vti02-fan-design-fable-corpus/20260923T011400-r3w0gf/00':
        _doc(1 / np.linspace(1 / 0.3, 1 / 10.0, 647), 1.0, 3.2, 50, 1.0, 0.9, 50e-6),
    'vti02-fan-design-sol-corpus/20260923T005529/00':
        _doc(1 / np.linspace(1 / 0.8, 1 / 10.0, 116), 3.2, 2.4, 25, 1.0, 1.8, 50e-6),
    'vti02-fan-design-sol-corpus/20260923T011408-tayua3/00':
        _doc(np.round(np.arange(1.5, 8.0001, 0.03), 4), 2.4, 3.2, 17, 1.0, 1.8, 100e-6),
    'vti02-fan-design-sol-corpus/20260923T011408-tayua3/01':
        _doc(1 / np.linspace(1 / 1.0, 1 / 10.0, 91), 3.2, 2.0, 61, 1.0, 1.8, 50e-6),
}
HAND_PROBE = {'vti02-fan-design-fable-none/20260923T010644-sf30z6/02'}  # 1D SdH check at n +3.8, 0->10 T


def _claude_tokens(tr):
    tok = dict(input=0, cache_creation=0, cache_read=0, output=0)
    if not tr.exists():
        return None
    for line in open(tr):
        if '"type":"result"' not in line and '"type": "result"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('type') != 'result':
            continue
        u = d.get('usage') or {}
        tok['input'] += u.get('input_tokens', 0) or 0
        tok['cache_creation'] += u.get('cache_creation_input_tokens', 0) or 0
        tok['cache_read'] += u.get('cache_read_input_tokens', 0) or 0
        tok['output'] += u.get('output_tokens', 0) or 0
    return tok


def _codex_tokens(ep):
    best = None
    for f in glob.glob(str(ep / 'codex-home/sessions/**/*.jsonl'), recursive=True):
        for line in open(f):
            if '"token_count"' not in line:
                continue
            d = json.loads(line)
            info = (d.get('payload') or {}).get('info') or {}
            t = info.get('total_token_usage')
            if t:
                best = t
    if best is None:
        return None
    return dict(input=max(0, best['input_tokens'] - best['cached_input_tokens']), cache_creation=0,
                cache_read=best['cached_input_tokens'], output=best['output_tokens'])


PRICES = {  # USD / 1M tokens: src/hera/replay/prices.toml (asof 2026-09-22)
    'gpt-6-astra': (10.0, 1.0, 50.0), 'gpt-5.6-sol': (4.0, 0.4, 20.0), 'gpt-5.6-luna': (0.2, 0.02, 1.2)}


def inventory():
    """Every episode under replay/runs/vti02-fan-design-*, classified. Pre-registered ending classes:
    fan | probe | b0 | none (counted) ; excluded:<reason> (reported, not placed) ; ungraded."""
    eps = []
    for rd in sorted(RUNS.glob('vti02-fan-design-*/*')):
        case_arm = rd.parent.name.replace('vti02-fan-design-', '')
        summ = {r['sample']: r for r in csv.DictReader(open(rd / 'summary.csv'))} if (rd / 'summary.csv').exists() else {}
        for epj in sorted(rd.glob('episodes/*/episode.json')):
            ep = epj.parent
            e = json.load(open(epj))
            run = e.get('run') or {}
            s = summ.get(ep.name, {})
            model = ((run.get('model') or {}).get('observed') or [None])[0] or (run.get('model') or {}).get('pinned')
            key = f"{rd.parent.name}/{rd.name}/{ep.name}"
            r = dict(key=key, case_arm=case_arm, corpus='corpus' if case_arm.endswith('corpus') else 'none',
                     model=MODEL_SHORT.get(model, model), model_id=model, effort=run.get('effort'),
                     runner=run.get('runner') or ('codex' if 'gpt' in str(model) else 'claude'),
                     cut=(e.get('cut') or {}).get('uuid', '')[:8], status=s.get('status', 'no_summary'),
                     stop_cell=s.get('stop_cell_sweeps', ''), cells=int(s.get('cells_appended') or 0),
                     stop=(s.get('stop') or '')[:40].replace('\n', ' '),
                     cost_summary=float(s['cost_usd']) if s.get('cost_usd') else None)
            gs = sorted(ep.glob('grades/fan-design/*/output.json'))
            doc = _load(gs[-1]) if gs else None
            r['source'] = 'grader' if doc else None
            if key in HAND:
                doc, r['source'] = HAND[key], 'hand'
            assert doc is None or g.check(doc) == [], (key, g.check(doc))
            r['doc'] = doc
            # ---- ending class (the pre-registered rule)
            excl = None
            if r['status'] in ('interrupted', 'quota', 'no_summary', 'error'):
                excl = 'harness:' + r['status']
            elif r['stop_cell'] == 'False':
                excl = 'harness:prep_cell_stop'
            elif r['cells'] == 0 and r['stop'].startswith('hera-watch'):
                excl = 'harness:watch_stub_prefix'  # watch armed before any cell; fixed in d7be0bf1
            if r['cut'] not in (CUT_0822, CUT_0821):
                excl = 'off_cut'
            if excl:
                r['ending'] = 'excluded:' + excl
            elif doc is not None and doc.get('status') == 'extracted' and g.tier_of(doc) == 'fan':
                r['ending'] = 'fan'
            elif doc is not None:
                r['ending'] = {'field_probe': 'probe', 'b0_cell': 'b0', 'none': 'none', 'fan': 'none'}.get(doc.get('landed'), 'none')
            elif key in HAND_PROBE:
                r['ending'], r['source'] = 'probe', 'hand'
            elif r['status'] == 'no_stop' and r['cells'] == 0:
                r['ending'] = 'none'
            else:
                r['ending'] = 'ungraded'
            # ---- cost / tokens
            if r['runner'] == 'codex':
                t = _codex_tokens(ep)
                r['tokens'] = t
                p = PRICES.get(model)
                r['cost_usd'] = (t['input'] * p[0] + t['cache_read'] * p[1] + t['output'] * p[2]) / 1e6 if (t and p) else r['cost_summary']
            else:
                r['tokens'] = _claude_tokens(ep / 'transcript.jsonl')
                r['cost_usd'] = r['cost_summary']
            r['session'] = ep / 'session'
            eps.append(r)
    return eps


def live_fans():
    out = []
    for d in sorted(LIVE.iterdir()):
        gs = sorted(d.glob('grades/fan-design/*/output.json'))
        if not gs:
            continue
        doc = _load(gs[-1])
        assert g.check(doc) == [], (d.name, g.check(doc))
        out.append(dict(key='live ' + d.name, doc=doc, session=d / 'session', ending='fan' if g.tier_of(doc) == 'fan' else 'probe'))
    return out


# ---------------------------------------------------------------- tones
_ks, _light = roi.ks, roi.light
def f_L(n):
    return np.array([roi.f_L(x) for x in np.atleast_1d(n)])

def f_light(n, tones='model'):
    n = np.atleast_1d(np.asarray(n, float))
    fm = np.interp(n, _ks, _light, left=np.nan, right=np.nan)
    if tones == 'model':
        return fm
    # empirical (live-check REPORT: F_light/F_L = 0.0394 n + 0.1235, fitted on 08-25 r8, n 1.2-3.05, e-side);
    # extrapolated linearly on the electron side, model tone kept on the hole side; NaN where the model is.
    fe = (0.0394 * np.abs(n) + 0.1235) * f_L(n)
    return np.where(np.isnan(fm), np.nan, np.where(n > 0, fe, fm))


# ---------------------------------------------------------------- acquisition
_comp = list(csv.DictReader(open(TOP / 'live-check/composite_columns.csv')))
_RB = np.array([float(r['nb']) for r in _comp if r['Rmax_nbhd']])
_RV = np.array([float(r['Rmax_nbhd']) for r in _comp if r['Rmax_nbhd']])
R_GLOBAL = 1557.54  # worst composite point (n 1.47, 10 T); used outside coverage

def r_max(n):
    """Predicted max |R| per column: composite neighbourhood max at the nearest 0.1 bin inside
    [0.9, 3.2] (actual frame); the global worst point outside (holes, n > 3.2)."""
    n = np.atleast_1d(n)
    inside = (n >= 0.85) & (n <= 3.25)
    idx = np.abs(_RB[None, :] - n[:, None]).argmin(1)
    return np.where(inside, _RV[idx], R_GLOBAL)

def acquisition(doc):
    li = {x['name']: x for x in doc['lockins']}
    L = li.get('sr1', doc['lockins'][0])
    tau, sens = float(L['time_constant_s']), L.get('sensitivity_V')
    I = doc['excitation_V'] / doc['bias_resistor_ohm']
    snr = min(1.0, I / 50e-9 * np.sqrt(tau / 0.3))
    quant = None
    if sens:
        lsb = 2.0 ** (np.ceil(np.log2(sens)) - 15)
        sigma = 40e-9 * np.sqrt(5.0 / (64.0 * tau))  # 40 nV/rtHz, 24 dB ENBW = 5/(64 tau)
        quant = bool(lsb / sigma >= 1.0)
    return dict(I=I, tau=tau, sens=sens, snr=snr, quant=quant)


# ---------------------------------------------------------------- scorer
DEFAULT = dict(k=3.0, clip=None, at2=0.0, cellw=1, tones='model')
Q_QUANT = 0.5  # free parameter: multiplier on a quantized channel (no dev-set design trips it)

def window(B, clip):
    B = np.unique(np.asarray(B, float))
    B = B[B >= max(1e-3, clip or 0.0)]
    return B

def score(B, n, knobs=None, acq=None):
    """Per-fan quality candidates. B: field axis (T); n: actual-frame densities (1e12).
    band   = #columns with F_L <= high line (m = 3 at the worst 1/B step in the window) and p >= k
    credit = sum_j c_j, c_j = 0 (p < k-1), at2 at p = k-1, linear to 1 at p = k, 1 above; F_L gate as band
    cells  = min(15, sum over tone cells of min(3, columns in the cell)) / 15, over band columns
    cells_acq = cells (clipped columns removed) x SNR x (Q_QUANT if quantized)"""
    kn = {**DEFAULT, **(knobs or {})}
    Bw = window(B, kn['clip'])
    n = np.asarray(n, float)
    z = dict(band=0, credit=0.0, cells=0.0, cells_acq=0.0, n_cells=0, W=0.0)
    if Bw.size < 2:
        return z
    W = 1 / Bw[0] - 1 / Bw[-1]
    hi = 1 / (3 * np.max(-np.diff(1 / Bw)))
    fl, FL = f_light(n, kn['tones']), f_L(n)
    ok = ~np.isnan(fl) & (FL <= hi)
    p = np.where(ok, fl * W, 0.0)
    k, a = kn['k'], kn['at2']
    c = np.where(p < k - 1, 0.0, np.where(p >= k, 1.0, a + (1 - a) * (p - (k - 1))))
    inband = ok & (p >= k)
    z.update(W=W, band=int(inband.sum()), credit=float(np.where(ok, c, 0.0).sum()))

    def capped(mask):
        if not mask.any():
            return 0.0, 0
        dF = kn['cellw'] / W
        f = fl[mask]
        cell = np.floor((f - f.min()) / dF + 1e-9).astype(int)
        cnt = np.bincount(cell)
        return min(15, np.minimum(3, cnt).sum()) / 15.0, int((cnt > 0).sum())
    z['cells'], z['n_cells'] = capped(inband)
    if acq is not None:
        clip_ok = np.ones_like(inband)
        if acq['sens']:
            clip_ok = acq['I'] * r_max(n) < 0.95 * acq['sens']
        ca, _ = capped(inband & clip_ok)
        z['cells_acq'] = ca * acq['snr'] * (Q_QUANT if acq['quant'] else 1.0)
        z['clipped_cols'] = int((inband & ~clip_ok).sum())
    return z


def design(r):
    """(B, n_actual, hours, acq) for a fan-tier episode."""
    doc = r['doc']
    try:
        case = g.case_of(Path(r['session']))
    except Exception:
        case = None
    if case is None or 'n_scale' not in case:
        import tomllib
        case = {'case': 'vti02-fan-design', **tomllib.load(open(g.CASES, 'rb'))['vti02-fan-design']}
    B = g.field_axis(doc, case)
    sc = case.get('n_scale', 1.0)
    n = sc * g.columns(doc) / 1e12
    h = g.derived(doc, B, g.columns(doc), sc, g.cost_model(case))['cost']['estimated_wall_h']
    if doc.get('form') == 'column_series':
        h *= 1 + len(doc.get('declared_columns_cm2') or [])
    return B, n, h, acquisition(doc)


def selftest():
    """score() at the default knobs == band.cells / band.credit on every graded fan."""
    bad = 0
    for r in [e for e in inventory() if e['ending'] == 'fan' and e['source'] == 'grader'] + live_fans():
        if r['ending'] != 'fan':
            continue
        B, n, h, acq = design(r)
        for clip in (None, 0.55, 1.0):
            fl = clip or 1e-3
            c0, _, _ = band.cells(B, n, fl)
            for a in (0.0, 0.25):
                cr = band.credit(B, n, fl, a)
                z = score(B, n, dict(clip=clip, at2=a))
                if z['band'] != c0 or abs(z['credit'] - cr) > 1e-9:
                    bad += 1
                    print('MISMATCH', r['key'], clip, a, z['band'], c0, z['credit'], cr)
    print('selftest mismatches:', bad)
    return bad


if __name__ == '__main__':
    selftest()
