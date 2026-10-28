"""Episode inventory, ending classes and the box scorer for the pre-registration study.

Read-only over $HERA_DATA. Scores with the repo's grader (hera/graders/fan-design: grade.py for the
design axes and hours, box.py for quality); `score()` at BASE is the grader's own box score.
"""
import csv, glob, importlib.util, json, sys, tomllib, warnings
from pathlib import Path
import numpy as np

warnings.filterwarnings('ignore')
TOP = Path('/data/sharpelab/hera-data/vti02-fan-scoring-v2')
GRADER = Path('/home/zack/sharpelab/measurement-env/hera/graders/fan-design')
_spec = importlib.util.spec_from_file_location('grade', GRADER / 'grade.py')
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)
box = g.box
RUNS = Path('/data/sharpelab/hera-data/replay/runs')
LIVE = Path('/data/sharpelab/hera-data/frontier/calibration/vti02-live')
OUT = TOP / 'prereg-stats'

CUT_0822 = '3a4cf818'  # the vti02-fan-design frontier of record
CUT_0821 = '45433bea'  # the earlier 08-21 cut the case used on 2026-09-22
MODEL_SHORT = {'claude-fable-5': 'fable', 'claude-opus-5': 'opus', 'claude-fable-5-1': 'fable51', 'claude-opus-5-5': 'opus55',
               'gpt-6-sol': 'gpt6sol', 'gpt-5.6-sol': 'sol', 'gpt-6-astra': 'astra',
               'claude-sonnet-5': 'sonnet', 'claude-haiku-4-5-20251001': 'haiku', 'gpt-5.6-luna': 'luna'}
MATRIX_MODELS = ('fable', 'opus', 'fable51', 'opus55', 'astra', 'gpt6sol')  # all four Claude models + two GPT-6
# $ per episode at effort high: measured on the vti02-fan-design dev set (fable, opus, astra), or the predecessor's
# measured token profile at the model's list price (fable51: Fable 5 with $0.25 cache reads; opus55: Opus 5 at
# $4 / $20, $0.20 reads; gpt6sol: GPT-5.6 Sol at $2 / $10, $0.20 cached).
EPISODE_USD = {'fable': 8.72, 'opus': 3.76, 'fable51': 6.24, 'opus55': 2.44, 'astra': 1.96, 'gpt6sol': 1.13}

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


# ---------------------------------------------------------------- box scorer
CASES_TOML = tomllib.load(open(g.CASES, 'rb'))
CASE = {'case': 'vti02-pre-fan-0822', **CASES_TOML['vti02-pre-fan-0822']}
BASE = dict(tone_model=CASE['tone_model'], b_lo_light=CASE['b_lo_light_T'], b_lo_split=CASE['b_lo_split_T'],
            signal_lockin=CASE['signal_lockin'], m=box.M, k=box.K, spacing=box.SPACING, cap=box.CAP)


def design(r):
    """(B, n actual in 1e12, hours) for a fan-tier episode, as the grader reads it."""
    doc = r['doc']
    case = g.case_of(Path(r['session']))
    if r.get('cut') == CUT_0821:  # the older 08-21 cut: its designs are in the 08-21 frame
        case = {**case, 'n_scale': CASES_TOML['vti02-live-0821']['n_scale']}
    B = g.field_axis(doc, case)
    sc = case.get('n_scale', 1.0)
    d = g.derived(doc, B, g.columns(doc), sc, g.cost_model(case))
    return B, sc * g.columns(doc) / 1e12, d['cost'].get('ladder', d['cost'])['estimated_wall_h']


def score(r, **knobs):
    """box.score at BASE overridden by knobs, for a fan-tier episode (design cached on r)."""
    if '_design' not in r:
        r['_design'] = design(r)
    B, n, h = r['_design']
    return box.score(np.asarray(B, float), n * 1e12, r['doc'], **{**BASE, **knobs}), h


def selftest():
    """score() at BASE == the grader's own box score on every fan the grader frames as design() does
    (all but the older 08-21 cut, which design() grades in its own frame)."""
    bad = 0
    for r in [e for e in inventory() if e['ending'] == 'fan' and e['cut'] != CUT_0821] + [e for e in live_fans() if e['ending'] == 'fan']:
        s, h = score(r)
        out = g.score(r['doc'], Path(r['session']))['scores']['box']
        if abs(out['quality'] - s['quality']) > 1e-12 or abs(out['hours'] - h) > 1e-12:
            bad += 1
            print('MISMATCH', r['key'], out['quality'], s['quality'], out['hours'], h)
    print('selftest mismatches:', bad)
    return bad


if __name__ == '__main__':
    selftest()
