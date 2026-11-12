"""Shared style for the pre-registration figures: the box-rescore palette, chrome and page furniture."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# the palette and chrome of box-rescore/figlib.py
BLUE, ORANGE, AQUA, YEL, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#4a3aa7'
INK, INK2, SURF, SOFT, HARD = '#0b0b0b', '#52514e', '#fcfcfb', '#ecebe6', '#d9d8d2'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#b5b4ae', 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF,
                     'axes.facecolor': SURF, 'font.family': 'DejaVu Sans'})

OUT = '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-figs/'
MUTED, GRID, AXIS = '#898781', '#e1e0d9', '#c3c2b7'
ARM = {'corpus': BLUE, 'none': ORANGE}
ARM_LABEL = {'corpus': 'with corpus', 'none': 'no corpus'}
MODEL_LABEL = {'fable': 'Fable 5', 'opus': 'Opus 5', 'fable51': 'Fable 5.1', 'opus55': 'Opus 5.5',
               'astra': 'GPT-6 Astra', 'gpt6sol': 'GPT-6 Sol', 'sol': 'GPT-5.6 Sol', 'luna': 'GPT-5.6 Luna',
               'sonnet': 'Sonnet 5', 'haiku': 'Haiku 4.5',
               'gpt-5.6-terra': 'GPT-5.6 Terra'}
MATRIX = ('fable', 'opus', 'fable51', 'opus55', 'astra', 'gpt6sol')
STATS = '/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats/'
DEV_NOTE = 'Development set, exploratory: the grader was developed on these episodes. No pre-registered data exist yet.'
plt.rcParams.update({'axes.grid': False, 'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.linewidth': 0.8,
                     'xtick.major.width': 0.8, 'ytick.major.width': 0.8, 'legend.frameon': False})


def page(w, h, title, sub, left=0.06, top_in=0.34):
    """A figure with its title block; returns (fig, y of the block's lower edge in figure fraction)."""
    fig = plt.figure(figsize=(w, h))
    y = 1 - top_in / h
    fig.text(left, y, title, fontsize=14, fontweight='bold', color=INK, va='top')
    y -= 0.30 / h
    fig.text(left, y, sub, fontsize=9.5, color=INK2, va='top', linespacing=1.45)
    return fig, y - (0.19 * (sub.count('\n') + 1) + 0.10) / h


def foot(fig, text, left=0.06, y_in=0.16, dev=False):
    fig.text(left, y_in / fig.get_figheight(), text, fontsize=8, color=MUTED, va='bottom', linespacing=1.45)
    if dev:
        fig.text(left, (y_in + 0.17 * (text.count('\n') + 1) + 0.06) / fig.get_figheight(), DEV_NOTE, fontsize=8.5,
                 color=INK, va='bottom', fontweight='bold')


def save(fig, name):
    fig.savefig(OUT + name, dpi=200, facecolor=SURF)
    print('wrote', OUT + name)
