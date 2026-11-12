import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

B = np.linspace(-2, 2, 2000)

def two_carrier(B, n1, mu1, n2, mu2):
    # sigma = n * |mu|, carrier type encoded in sign of mu
    sxx = n1*abs(mu1)/(1+(mu1*B)**2) + n2*abs(mu2)/(1+(mu2*B)**2)
    sxy = n1*mu1*abs(mu1)*B/(1+(mu1*B)**2) + n2*mu2*abs(mu2)*B/(1+(mu2*B)**2)
    denom = sxx**2 + sxy**2
    return sxx/denom, -sxy/denom

# Initial parameters: one hole-like, one electron-like
init = dict(n1=1.0, mu1=10.0, n2=0.5, mu2=-5.0)

fig, (ax_ryx, ax_rxx) = plt.subplots(1, 2, figsize=(12, 5))
plt.subplots_adjust(bottom=0.45, hspace=0.4)

Rxx0, Ryx0 = two_carrier(B, **init)
line_ryx, = ax_ryx.plot(B, Ryx0, 'C0')
line_rxx, = ax_rxx.plot(B, Rxx0, 'C0')

ax_ryx.axhline(0, color='k', lw=0.5, ls='--')
ax_ryx.axvline(0, color='k', lw=0.5, ls='--')
ax_rxx.axvline(0, color='k', lw=0.5, ls='--')

ax_ryx.set_xlabel('$B$ (T)')
ax_ryx.set_ylabel(r'$R_{yx}$ (arb.)')
ax_ryx.set_title('Hall (antisymmetric)')

ax_rxx.set_xlabel('$B$ (T)')
ax_rxx.set_ylabel(r'$R_{xx}$ (arb.)')
ax_rxx.set_title('Longitudinal (symmetric)')

# Sliders
slider_specs = [
    ('n1',  0.34, r'$n_1$ (arb.)',          0.01, 5.0,   init['n1']),
    ('mu1', 0.26, r'$\mu_1$ (T$^{-1}$)',   -200,  200,   init['mu1']),
    ('n2',  0.18, r'$n_2$ (arb.)',           0.01, 5.0,   init['n2']),
    ('mu2', 0.10, r'$\mu_2$ (T$^{-1}$)',   -200,  200,   init['mu2']),
]

sliders = {}
for key, y, label, vmin, vmax, v0 in slider_specs:
    ax_sl = plt.axes([0.15, y, 0.7, 0.04])
    sliders[key] = Slider(ax_sl, label, vmin, vmax, valinit=v0)

def update(_):
    n1  = sliders['n1'].val
    mu1 = sliders['mu1'].val
    n2  = sliders['n2'].val
    mu2 = sliders['mu2'].val

    Rxx, Ryx = two_carrier(B, n1, mu1, n2, mu2)
    line_ryx.set_ydata(Ryx)
    line_rxx.set_ydata(Rxx)

    for ax, data in [(ax_ryx, Ryx), (ax_rxx, Rxx)]:
        pad = np.ptp(data) * 0.1 or 0.1
        ax.set_ylim(data.min() - pad, data.max() + pad)

    fig.canvas.draw_idle()

for sl in sliders.values():
    sl.on_changed(update)

plt.show()
