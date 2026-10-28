# Runs 6 and 7: raw four-probe Rxx versus measured B, before spectral interpretation.
from hera.analysis import resolve_channels
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
spot = {}
for ax, rid in zip(axes, (6, 7)):
    r = run(rid)
    channels = {ch.cid: ch for ch in resolve_channels(r.meta)}
    I = r.col(channels['sr0'].col) / channels['sr0'].gain
    R = np.abs((r.col(channels['sr1'].col) / channels['sr1'].gain) / I)
    B = r.col('magnet_field')
    ix = np.argsort(B)
    spot[rid] = (B[ix], R[ix])
    ax.plot(B, R, lw=.7)
    ax.set(xlabel='measured B (T)', ylabel='|Rxx| (ohm)', title=f'data/{rid}: raw')
    print(f'data/{rid}: {len(B)} points, B {B.min():.3f}..{B.max():.3f} T, R {R.min():.1f}..{R.max():.1f} ohm, I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, interrupted={r.interrupted}')
fig.tight_layout(); plt.show()
