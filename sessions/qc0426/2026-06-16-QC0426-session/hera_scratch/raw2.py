m=load_meta(2);ci={c:i for i,c in enumerate(m['columns'])};d=load1d(2)
B=d[:,ci['magnet_mag']];Ib=5e-9;I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
fig,ax=plt.subplots(1,3,figsize=(15,4))
ax[0].plot(B,d[:,ci['sr1_X']]/Ib,label='sr1');ax[0].plot(B,d[:,ci['sr2_X']]/Ib,label='sr2')
ax[0].set(xlabel='B (T)',ylabel='Rxx (ohm)');ax[0].legend()
ax[1].plot(B,d[:,ci['sr3_X']]/Ib,'C2');ax[1].set(xlabel='B (T)',ylabel='Rxy (ohm)')
ax[2].plot(B,I*1e9);ax[2].set(xlabel='B (T)',ylabel='I_drain (nA)')
fig.suptitle('Raw — file 2: go/no-go B-sweep (n=-4e12, D=0, sens 2mV)');plt.tight_layout();plt.show()
