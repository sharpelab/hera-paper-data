# Step 0 (runs 1,2) — effective-zero field B_eff0: stitch two one-sided halves, fit dip center
def _load(i):
    gg = run(i)
    B = gg.col_at(gg.col_indices('magnet_field')[0]) * 1e3
    R = (gg.col_at(gg.col_indices('sr830_3_X')[0]) / 100) / 1e-9
    return B, R, gg
B1, R1, g1 = _load(1)   # +5 -> 0
B2, R2, g2 = _load(2)   # -5 -> 0
B = np.concatenate([B2, B1]); R = np.concatenate([R2, R1])
o = np.argsort(B); B, R = B[o], R[o]

Rn = np.median(R[np.abs(B) > 3.5]); thr = 0.5*Rn
def _flank(side_B, side_R, sign):
    order = np.argsort(sign*side_B); bb, rr = side_B[order], side_R[order]
    for k in range(1, len(rr)):
        if rr[k-1] < thr <= rr[k]:
            f = (thr-rr[k-1])/(rr[k]-rr[k-1]); return bb[k-1]+f*(bb[k]-bb[k-1])
    return np.nan
Bm = _flank(B[B<0], R[B<0], -1); Bp = _flank(B[B>0], R[B>0], +1)
B0_thr = 0.5*(Bm+Bp)
near = np.abs(B - B0_thr) < 1.5; c = np.polyfit(B[near], R[near], 2); B0_par = -c[1]/(2*c[0])
B_EFF0_mT = 0.5*(B0_thr + B0_par)
print(f"normal Rxx ~ {Rn:.1f} ohm; half-normal crossings B-={Bm:.3f} B+={Bp:.3f} mT")
print(f"B_eff0: midpoint {B0_thr:.3f} / parabola {B0_par:.3f} -> FINAL {B_EFF0_mT:.3f} mT")
print(f"B_c half-width ~ {0.5*(Bp-Bm):.2f} mT (cf prior B_c_perp ~1.8 mT)")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(B1, R1, '-o', ms=3, label='+5->0 (run 1)', color='C0')
ax.plot(B2, R2, '-o', ms=3, label='-5->0 (run 2)', color='C1')
ax.axvline(B_EFF0_mT, color='r', ls='--', lw=1, label=f'B_eff0 = {B_EFF0_mT:.2f} mT')
ax.axvline(0, color='k', lw=0.5, ls=':')
ax.axhline(thr, color='gray', lw=0.6, ls=':', label='half-normal')
ax.set_xlabel('B$_\\perp$ (mT)'); ax.set_ylabel('R$_{xx}$ 4T (30-31)  ($\\Omega$)')
ax.set_title('Step 0 — field-kill dip, B_eff0 calibration'); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
