# Run 8 — onset + FFT read vs F_L and the forward model
import sys
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/trilayer_fs_count"))
from fs_count_b0 import aba_fs, abc_fs
from hera.analysis import sdh_onset

g = run(8)
B = g.col("magnet_field")
i_dr = np.abs(g.col("sr0_X")) / 1e6
FL = 18.6  # (h/4e)*1.8e16, geometry-anchored scale

# onset per channel (r_full_scale so a soft-clip truncates, not corrupts)
for ch, fs in (("sr1", 200e-6), ("sr3", 200e-6)):
    R = g.col(f"{ch}_X") / i_dr
    try:
        on = sdh_onset(R, B, r_full_scale=fs / 1e-9)
        print(f"--- {ch} ---"); print(on.summary())
    except Exception as e:
        print(f"--- {ch} --- {type(e).__name__}: {e}")

# FFT: stability sweep + all channels vs F_L
fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
R1 = (g.col("sr1_X") / i_dr)[:, None]
for bg in (4, 5, 6):
    for lo in (1.7, 2.2):
        f, s = sdh_fft(R1, B, b_range=(lo, 9.0), bg_degree=bg)
        axs[0].plot(f, s[0] / s[0].max(), lw=0.8, label=f"bg{bg}, B>{lo}")
axs[0].set_title("sr1 stability sweep")
for ch, off in (("sr1", 0), ("sr2", 1.1), ("sr3", 2.2)):
    Rc = (g.col(f"{ch}_X") / i_dr)[:, None]
    f, s = sdh_fft(Rc, B, b_range=(1.7, 9.0), bg_degree=5)
    axs[1].plot(f, s[0] / s[0].max() + off, lw=0.9, label=ch)
axs[1].set_title("all channels (offset)")
# model overlays: ABA pair (hole side) and ABC singleton
efa, orb = aba_fs(-1.8e16)
for F, _ in orb:
    axs[1].axvline(F, color="g", ls="-.", lw=0.8)
_, _, _, _, Ftot = abc_fs(-1.8e16)
axs[1].axvline(Ftot, color="m", ls="-.", lw=0.8)
for ax in axs:
    ax.axvline(FL, color="r", ls="--", lw=0.8, label="F_L")
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.grid(alpha=0.3); ax.legend(fontsize=6)
plt.show()
print(f"model: ABA pair {[f'{F:.1f}' for F, _ in orb]} T (green), ABC singleton {Ftot:.1f} T (magenta), F_L={FL} (red)")
