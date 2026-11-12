import os
F=38
m=load_meta(F);ci={c:i for i,c in enumerate(m['columns'])}
fn=f"{file_path}/{F}/data.tsv.gz" if os.path.exists(f"{file_path}/{F}/data.tsv.gz") else f"{file_path}/{F}/data.tsv"
d=np.loadtxt(fn); B=d[:,ci['magnet_mag']]; Ib=5e-9; I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
fig,ax=plt.subplots(1,3,figsize=(16,4.2))
ax[0].plot(B,d[:,ci['sr1_X']]/Ib,'.-',ms=2,label='sr1 T3-T4');ax[0].plot(B,d[:,ci['sr2_X']]/Ib,'.-',ms=2,label='sr2 B4-B5')
ax[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title='raw Rxx(B)');ax[0].legend()
ax[1].plot(B,d[:,ci['sr3_X']]/Ib,'.-',ms=2,color='C2');ax[1].set(xlabel='B (T)',ylabel='Rxy sr3 (ohm)',title='raw Rxy(B)')
ax[2].plot(B,I*1e9,'.-',ms=2,color='C3');ax[2].axhline(5,ls=':',c='k');ax[2].set(xlabel='B (T)',ylabel='I_drain B7 (nA)',title='drain B7')
fig.suptitle(f'Electron side 12.5 mT (4x), n=+8e12, D=0, drain B7, Si=+50V, 200uV (file 38, {d.shape[0]} pts)');plt.tight_layout();plt.show()
print(f'{d.shape[0]} pts, B to {B.max():.2f} T; drain med {np.median(I)*1e9:.2f} nA')
