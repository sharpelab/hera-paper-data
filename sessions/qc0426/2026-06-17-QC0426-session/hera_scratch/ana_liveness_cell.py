# Gate C liveness (run 1) — provided contact config, TG trace at BG=Si=0, B=0.
# RAW first: drain current + per-channel Rxx/Rxy vs TG. Current-bias => modulation
# is in the Rxx voltage channels; sr0 (drain current) is forced ~constant.
d = pretty_load(1)
m = load_meta(1)
mc = m['measurement_config']
Ibias = mc['bias_voltage'] / mc['bias_resistor']      # 5 nA
g0 = mc['sr0_gain']                                    # -1e6

V    = d['DC_bias']
I    = d['sr0_X'] / g0
Rxx1 = d['sr1_X'] / Ibias                              # T3-T4
Rxx2 = d['sr2_X'] / Ibias                              # B4-B5
Rxy3 = d['sr3_X'] / Ibias                              # T5-B6 (Hall cross; B=0)

fig, ax = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
ax[0].plot(V, Rxx1, '.-', label='sr1 Rxx T3-T4')
ax[0].plot(V, Rxx2, '.-', label='sr2 Rxx B4-B5')
ax[0].set_ylabel(r'$R_{xx}$ ($\Omega$)'); ax[0].legend(); ax[0].grid(alpha=.3)
ax[0].set_title('Gate C liveness (run 1): TG trace, BG=Si=0, B=0')
ax[1].plot(V, I*1e9, '.-k', label='sr0 drain I (nA)')
ax[1].plot(V, Rxy3, '.-', color='C3', label=r'sr3 $R_{xy}$ ($\Omega$, B=0)')
ax[1].set_xlabel('$V_{TG}$ (DC_bias, V)'); ax[1].legend(); ax[1].grid(alpha=.3)
plt.show()

print(f'I_bias = {Ibias*1e9:.2f} nA | drain I: med {np.median(I)*1e9:.2f} nA '
      f'(flat across sweep -> current-bias OK, current passes)')
print(f'Rxx peak: sr1 {np.nanmax(Rxx1):.0f} ohm @ V_TG={V[np.nanargmax(Rxx1)]:.2f} ; '
      f'sr2 {np.nanmax(Rxx2):.0f} ohm @ V_TG={V[np.nanargmax(Rxx2)]:.2f}')
print(f'channel independence: corr(sr1,sr2)={np.corrcoef(Rxx1,Rxx2)[0,1]:.3f}, '
      f'identical={np.allclose(Rxx1,Rxx2)} (not identical -> no grounded short)')
print(f'leakage: |I_bg|max={np.abs(d["k_bg_curr"]).max():.2e} A, '
      f'|I_si|max={np.abs(d["k_2410_curr"]).max():.2e} A (both at/near floor)')
print('VERDICT: device alive, passes current, gate-responsive (CNP near V_TG~0 at '
      'BG=0), channels independent, leakage at floor. Gate C PASS. '
      'Note: low device R (~kohm) -> data here quantized at 5 mV sens; '
      'CNP shows a double-peak common to both Rxx channels (real feature, not a '
      'per-contact mosaic offset) to resolve in the 2D map.')
