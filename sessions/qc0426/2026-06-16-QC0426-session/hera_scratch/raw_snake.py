# Raw — Aaron snake (files 36 hole / 37 electron), n=+/-8e12, Si=+50V, 200uV
fig,ax=plt.subplots(1,3,figsize=(16,4.5))
for F,side,c in [(36,'hole n=-8e12','C0'),(37,'electron n=+8e12','C1')]:
    m=load_meta(F);ci={k:i for i,k in enumerate(m['columns'])};d=load1d(F)
    B=d[:,ci['magnet_mag']];Ib=5e-9;I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
    ax[0].plot(B,d[:,ci['sr1_X']]/Ib,'.-',ms=2,label=f'sr1 {side}')
    ax[1].plot(B,d[:,ci['sr3_X']]/Ib,'.-',ms=2,label=f'sr3 {side}')
    ax[2].plot(B,I*1e9,'.-',ms=2,label=f'I_drain(B7) {side}')
ax[0].set(xlabel='B (T)',ylabel='Rxx sr1 (ohm)',title='raw Rxx(B)');ax[0].legend(fontsize=7)
ax[1].set(xlabel='B (T)',ylabel='Rxy sr3 (ohm)',title='raw Rxy(B)');ax[1].legend(fontsize=7)
ax[2].set(xlabel='B (T)',ylabel='I (nA)',title='drain B7 (alive both legs)');ax[2].legend(fontsize=7)
fig.suptitle('Raw — Aaron snake, drain B7, Si=+50V, 200uV (B7 survived)');plt.tight_layout();plt.show()
print('B7 alive both legs; clean smooth Rxx at 200uV')
