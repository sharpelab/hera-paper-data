"""Figure 2: one fan, three numbers. Two panels cut from box-rescore/fig/3_live_fans.png, with their grades.

Grades from box-rescore/rescore.md (the grader's box score).
"""
from PIL import Image
from style import *

SRC = '/data/sharpelab/hera-data/vti02-fan-scoring-v2/box-rescore/fig/3_live_fans.png'
KEY = (150, 219, 1687, 317)                                # pixel boxes in SRC: left, top, right, bottom
FANS = [('08-22 run 8: Fable 5 with corpus, live', (100, 493, 1687, 953), '1.00', '3.8 h', '0.81',
         'A fine 1/B grid from 1 T: both tones sampled, the window long enough to split them.'),
        ('08-24 run 4: Opus 5, no corpus, live', (100, 1488, 1687, 1965), '0.00', '1.2 h', '0.16',
         'The 1/B steps are too coarse for F_L and the fan stops at 6 T: the split earns nothing.')]
im = Image.open(SRC).convert('RGB')
W, H = 11.0, 11.3
fig, ytop = page(W, H, 'One fan, three numbers: the chance it makes the call, its hours, its quality',
                 'The grader reads the planned design only: field rows, density columns, current and time constant. '
                 'Two fans measured live on vti-02,\nwith their measured data (left) and the grade drawn on their '
                 'Fourier maps (right).', left=0.3 / W)
LM, PW = 0.3, 10.4                                         # left margin and picture width, inches


def picture(box, top_in):
    """Place a crop PW wide with its top edge top_in below the figure's top; returns its height in inches."""
    crop = im.crop(box)
    h = PW * crop.height / crop.width
    ax = fig.add_axes([LM / W, 1 - (top_in + h) / H, PW / W, h / H])
    ax.imshow(crop, interpolation='lanczos', aspect='auto'); ax.axis('off')
    return h


y = (1 - ytop) * H + 0.05
for name, box, p_call, hours, quality, why in FANS:
    fig.text(LM / W, 1 - (y + 0.12) / H, name, fontsize=11, fontweight='bold', color=INK, va='center')
    fig.text(LM / W, 1 - (y + 0.40) / H, why, fontsize=9, color=INK2, va='center')
    for k, (lab, val) in enumerate((('P(call)', p_call), ('measurement time', hours), ('quality', quality))):
        x = (6.6 + k * 1.5) / W
        fig.text(x, 1 - (y + 0.08) / H, lab, fontsize=8.5, color=INK2, va='center')
        fig.text(x, 1 - (y + 0.38) / H, val, fontsize=16, fontweight='semibold', color=INK, va='center')
    y += 0.62
    y += picture(box, y) + 0.30
fig.text(LM / W, 1 - (y + 0.05) / H, 'Key to the right-hand panels', fontsize=9, color=INK, fontweight='bold', va='center')
y += 0.15
y += picture(KEY, y)
foot(fig, 'P(call): each part (the light tone; the F_L / F_heavy split) counts its independent detected columns, one '
     'counting little and four making the call; the fan takes its lesser part. Quality = A × (light + split) / 14.\nHours from the rig cost model. Panels from '
     'box-rescore/fig/3_live_fans.png; grades from box-rescore/rescore.md.', left=0.3 / W, dev=True)
save(fig, 'fig2_one_fan.png')
print('used height', round(y, 2), 'of', H)
