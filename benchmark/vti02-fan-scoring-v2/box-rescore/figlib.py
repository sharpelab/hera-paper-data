"""Shared pieces for the explainer figures."""
import sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
sys.argv = [sys.argv[0], '/data/sharpelab/hera-data/vti02-fan-scoring-v2']
import numpy as np, common as C, importlib.util
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
spec = importlib.util.spec_from_file_location('box', '/home/zack/sharpelab/measurement-env/hera/graders/fan-design/box.py')
box = importlib.util.module_from_spec(spec); spec.loader.exec_module(box)
BLUE, ORANGE, AQUA, YEL, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#4a3aa7'
INK, INK2, SURF, SOFT, HARD = '#0b0b0b', '#52514e', '#fcfcfb', '#ecebe6', '#d9d8d2'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#b5b4ae', 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF,
                     'axes.facecolor': SURF, 'font.family': 'DejaVu Sans'})
OUT = '/data/sharpelab/hera-data/vti02-fan-scoring-v2/box-rescore/fig/'

def all_fans():
    return {r['key']: r for r in C.inventory() + C.live_fans() if r.get('ending') == 'fan'}

def columns(r):
    """Everything a panel needs for one fan."""
    B, n, h = C.design(r); B = np.unique(np.asarray(B)[np.asarray(B) > 0]); n = np.asarray(n)
    s = box.score(B, n * 1e12, r['doc'], b_lo_light=0.75, b_lo_split=1.0, tone_model='Halder_ABAB', signal_lockin='sr1')
    WLd, WSd = box.window(B, 0.75), box.window(B, 1.0)
    fl = box.f_light(n, 'Halder_ABAB'); e = (n > 0) & ~np.isnan(fl); f = np.where(e, fl, 0.0)
    wl = np.where(e, box.ramp(f * box.w_eff(f, WLd['intervals'], box.M), box.K), 0.0)
    ws = np.where(e, box.ramp(f * box.w_eff(box.FLN * np.where(e, n, 0), WSd['intervals'], box.M), box.K), 0.0)
    return dict(B=B, n=n, h=h, s=s, fl=fl, e=e, WL=WLd['W_per_T'], WS=WSd['W_per_T'], du_l=WLd['intervals'],
                du_s=WSd['intervals'], wl=wl, ws=ws)
