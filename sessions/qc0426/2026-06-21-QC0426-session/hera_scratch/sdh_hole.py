import os, numpy as np, hera.analysis as a
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "1"))
B = run.col("magnet_field")
I = run.col("sr0_X") / (-1e6)          # measured drain current
R1 = run.col("sr1_X") / I              # gain_V = 1
R2 = run.col("sr2_X") / I
Rxy = run.col("sr3_X") / I
print(f"N={len(B)}  B [{B.min():.3f},{B.max():.3f}] T   I med={np.median(I)*1e9:.2f} nA")

# Clip detection: sr1_X railed near 1e-5 FS
x1 = np.abs(run.col("sr1_X")); fs = 1e-5
clip = x1 >= 0.95*fs
B_clip = B[clip].min() if clip.any() else B.max()
print(f"sr1 clip (|X|>=9.5uV) starts at B={B_clip:.3f} T; {clip.sum()}/{len(B)} pts clipped")
clean = B < B_clip*0.98

# Onset on clean Rxx (sr1)
onset = a.sdh_onset(R1[clean], B[clean])
ob = getattr(onset, "onset_b", None); chb = getattr(onset, "clip_high_b", None)
cf = getattr(onset, "consensus_freq", None)
print(f"sdh_onset: onset_b={ob}  clip_high_b={chb}  consensus_freq={cf}")

# F_L reference
n = -3.0e16
FL = float(a.luttinger_frequency(n))
print(f"F_L (n=3e12) = {FL:.2f} T")

# FFTs
def fft1d(R, Bv, lo, hi, deg=5):
    f, mag = a.sdh_fft(R.reshape(-1,1), Bv, b_range=(lo, hi), bg_degree=deg)
    return f, mag[0]
lo_cut = max(0.4, ob if ob else 0.4)
f_xx, m_xx = fft1d(R1[clean], B[clean], lo_cut, B[clean].max())
f_xx2, m_xx2 = fft1d(R2[clean], B[clean], lo_cut, B[clean].max())
# Rxy clean to 7.9 T (sr3 not clipped) — high-field SdH content
f_xy, m_xy = fft1d(Rxy, B, lo_cut, B.max())

def top_peaks(f, m, fmin=5, n=5):
    from scipy.signal import find_peaks
    sel = f > fmin
    fs, ms = f[sel], m[sel]
    pk, _ = find_peaks(ms)
    if len(pk) == 0:
        return []
    order = pk[np.argsort(ms[pk])[::-1][:n]]
    return sorted([(round(float(fs[i]), 1), round(float(ms[i]), 2)) for i in order])
print("\nRxx sr1 FFT peaks (f[T], mag):", [(round(p[0],1),round(p[1],2)) for p in top_peaks(f_xx,m_xx)])
print("Rxx sr2 FFT peaks:", [(round(p[0],1),round(p[1],2)) for p in top_peaks(f_xx2,m_xx2)])
print("Rxy sr3 FFT peaks (clean to 7.9T):", [(round(p[0],1),round(p[1],2)) for p in top_peaks(f_xy,m_xy)])

# --- Plots ---
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
ax[0,0].plot(B, R1, label="sr1 Rxx"); ax[0,0].plot(B, R2, label="sr2 Rxx"); ax[0,0].axvline(B_clip, c='r', ls=':', label=f"clip {B_clip:.2f}T")
ax[0,0].set_xlabel("B [T]"); ax[0,0].set_ylabel("Rxx [Ω]"); ax[0,0].set_title("Raw Rxx(B)"); ax[0,0].legend()
ax[0,1].plot(B, -Rxy, c='g'); ax[0,1].set_xlabel("B [T]"); ax[0,1].set_ylabel("-Rxy [Ω]"); ax[0,1].set_title("Raw -Rxy(B) (clean to 7.9T)")
# bg-subtracted ΔRxx vs 1/B (clean window)
m = clean & (B>lo_cut)
bb = B[m]; rr = R1[m]
bg = np.polyval(np.polyfit(bb, rr, 5), bb)
ax[1,0].plot(1/bb, rr-bg); ax[1,0].set_xlabel("1/B [1/T]"); ax[1,0].set_ylabel("ΔRxx sr1 [Ω]"); ax[1,0].set_title(f"sr1 SdH, 1/B (B {lo_cut:.2f}-{bb.max():.2f}T)")
ax[1,1].plot(f_xx, m_xx, label="sr1 Rxx"); ax[1,1].plot(f_xx2, m_xx2, label="sr2 Rxx"); ax[1,1].plot(f_xy, m_xy, label="sr3 Rxy(7.9T)", alpha=0.7)
ax[1,1].axvline(FL, c='k', ls='--', label=f"F_L={FL:.0f}T")
ax[1,1].set_xlim(0, FL*1.6); ax[1,1].set_xlabel("Frequency [T]"); ax[1,1].set_ylabel("FFT mag"); ax[1,1].set_title("1/B FFT"); ax[1,1].legend()
fig.suptitle(f"Run 1 — hole SdH spot check n=-3e12, D=0 (clip>{B_clip:.1f}T on Rxx)")
fig.tight_layout(); out=os.path.join(SCR,"run1_sdh_hole.png"); fig.savefig(out,dpi=110); print("saved",out)
