from hera.analysis import resolve_channels, sdh_onset, sdh_fft
from scipy.signal import find_peaks

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for rid, side in [(6, "electron"), (7, "hole")]:
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    order = np.argsort(B)
    ax[0, 0].plot(B[order], R[order], lw=0.8, label=f"{rid} {side}")
    ax[0, 1].plot(B[order], I[order] * 1e9, lw=0.8, label=f"{rid} {side}")
    ax[1, 0].plot(B[order], r.col("k_2400_tg_curr")[order]*1e12, lw=0.8, label=f"{rid} TG")
    ax[1, 1].plot(B[order], r.col("k_2400_bg_curr")[order]*1e12, lw=0.8, label=f"{rid} BG")
    print(f"data/{rid}: {r.rows} points, {(r.meta['end_time']-r.meta['start_time'])/60:.1f} min, "
          f"B {B[0]:.2f}→{B[-1]:.2f} T, R {np.nanmin(R):.1f}…{np.nanmax(R):.1f} Ω, "
          f"I_drain {np.nanmin(I)*1e9:.3f}…{np.nanmax(I)*1e9:.3f} nA, "
          f"T {np.nanmin(r.col('T_sample')):.3f}…{np.nanmax(r.col('T_sample')):.3f} K, "
          f"interrupted={r.interrupted}")
for a, yl in zip(ax.flat, ["|Rxx| (Ω)", "I_drain (nA)", "I_TG (pA)", "I_BG (pA)"]):
    a.set(xlabel="B (T)", ylabel=yl); a.legend(fontsize=7)
fig.suptitle("Raw run-6/7 spot traces; measured-current resistance")
fig.tight_layout(); plt.show()

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for j, rid in enumerate((6, 7)):
    r = run(rid); ch = {c.cid:c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain
    R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/I)
    order = np.argsort(B); B, R = B[order], R[order]
    onset = sdh_onset(R, B, b_lo=0.3, b_hi=10, r_full_scale=10000)
    print(f"\ndata/{rid}: {onset.summary()}")
    f, spec = sdh_fft(R[:,None], B, b_range=(1.5, 10), nfft=2048, bg_degree=5, log=False)
    pk, _ = find_peaks(spec[0]); pk = sorted((p for p in pk if 2 < f[p] < 80), key=lambda p:spec[0,p], reverse=True)[:5]
    print("FFT peaks 1.5–10 T (T):", [round(float(f[p]),1) for p in pk])
    ax[j].plot(f, spec[0]); ax[j].set(xlim=(0,75), xlabel="SdH frequency (T)", ylabel="FFT amplitude (arb.)", title=f"data/{rid}: 1.5–10 T")
    for p in pk[:3]: ax[j].axvline(f[p], color="k", ls=":", alpha=.35)
fig.tight_layout(); plt.show()
