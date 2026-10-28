# CNP ridge per Rxx channel -> CNP-line fit -> (n, D) calibration
import scipy.ndimage as ndi
from sharpelab_nb import gates

def cnp_ridge(R, tg, smooth=1.5):
    out = []
    for row in R:
        rs = ndi.gaussian_filter1d(row, smooth)
        out.append(tg[rs >= 0.98 * rs.max()].mean())   # railed-plateau-robust center
    return np.array(out)

fits = {}
for ch in ['sr1', 'sr2']:
    tgc = cnp_ridge(Rxx[ch], tg0)
    s, b = np.polyfit(bg0, tgc, 1)
    fits[ch] = dict(tgc=tgc, slope=s, b=b, resid=tgc - (s * bg0 + b))

RATIO = -float(np.mean([fits[c]['slope'] for c in fits]))     # c_bg/c_tg
B_INT = float(np.mean([fits[c]['b'] for c in fits]))
C_TG = gates.stack_capacitance([(15.6, 3)])                   # geometry anchor (15.6 nm hBN)
C_BG = RATIO * C_TG                                            # data-calibrated ratio
N_OFF = -gates.calc_nD(B_INT, 0.0, C_TG, C_BG)[0]             # 1e12 cm^-2, sets n=0 on CNP line
cal = GateCalibration(C_TG, C_BG, n_offset=N_OFF * 1e16, D_offset=0.0)   # SI, for downstream cells

clos = {ch: np.abs(gates.calc_nD(fits[ch]['tgc'], bg0, C_TG, C_BG, N_OFF, 0)[0]).max() for ch in fits}

# D = 0 line, gate-limited window (drop out-of-range, never clamp)
ns = np.linspace(-12, 12, 4001)
Vtg0, Vbg0 = gates.calc_gate_voltages(ns, ns * 0, C_TG, C_BG, N_OFF, 0)
keep = (Vtg0 >= -6) & (Vtg0 <= 7) & (Vbg0 >= -4.5) & (Vbg0 <= 4.5)

fig, ax = plt.subplots(1, 3, figsize=(16, 4.4))
for a_, ch in zip(ax[:2], ['sr1', 'sr2']):
    pc = a_.pcolormesh(tg0, bg0, np.clip(Rxx[ch], 0, 4400), shading='auto', cmap='inferno')
    a_.plot(fits[ch]['tgc'], bg0, 'c.', ms=4, label='ridge')
    a_.plot(fits[ch]['slope'] * bg0 + fits[ch]['b'], bg0, 'w-', lw=1, label='fit')
    a_.plot(Vtg0[keep], Vbg0[keep], 'g--', lw=1.2, label='D=0')
    a_.set_xlabel('V_tg (V)'); a_.set_ylabel('V_bg (V)')
    a_.set_title(f"{ch}: c_bg/c_tg={-fits[ch]['slope']:.3f}"); a_.legend(fontsize=7, loc='upper right')
    fig.colorbar(pc, ax=a_)
for ch in fits:
    ax[2].plot(bg0, fits[ch]['resid'] * 1e3, '.-', label=f"{ch} rms={fits[ch]['resid'].std()*1e3:.0f}mV")
ax[2].axhline(0, color='k', lw=.5); ax[2].set_xlabel('V_bg (V)'); ax[2].set_ylabel('fit resid (mV)')
ax[2].set_title('CNP-line residuals'); ax[2].legend(fontsize=8)
plt.tight_layout(); plt.show()

print(f"ratio c_bg/c_tg = {RATIO:.4f}   (sr1 {-fits['sr1']['slope']:.4f}, sr2 {-fits['sr2']['slope']:.4f}; agree {abs(fits['sr1']['slope']-fits['sr2']['slope'])/RATIO*100:.1f}%)")
print(f"c_tg = {C_TG:.4e} F/m^2 (geometry)    c_bg = {C_BG:.4e} F/m^2 (ratio)")
print(f"CNP intercept b = {B_INT:+.4f} V    n_offset = {N_OFF:+.4f}e12 cm^-2    D_offset = 0 (assumed)")
print(f"closure max|n| @ extracted ridge: sr1 {clos['sr1']:.3f}, sr2 {clos['sr2']:.3f} e12 cm^-2")
print(f"D=0 gate-limited window: n in [{ns[keep].min():+.2f}, {ns[keep].max():+.2f}]e12 cm^-2  (Onsager model valid <=3.5e12)")
