m=load_meta(0);ci={c:i for i,c in enumerate(m['columns'])};d=load1d(0)
v=d[:,ci['DC_bias']];Ib=5e-9;I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
fig,ax=plt.subplots(1,3,figsize=(15,4))
ax[0].plot(v,d[:,ci['sr1_X']]/Ib,label='sr1');ax[0].plot(v,d[:,ci['sr2_X']]/Ib,label='sr2')
ax[0].set(xlabel='TG (V)',ylabel='Rxx (ohm)');ax[0].legend()
ax[1].plot(v,d[:,ci['sr3_X']]/Ib,'C2');ax[1].set(xlabel='TG (V)',ylabel='Rxy (ohm)')
ax[2].plot(v,d[:,ci['k_bg_curr']]*1e9,label='k_bg');ax[2].plot(v,d[:,ci['k_2410_curr']]*1e9,label='Si')
ax[2].set(xlabel='TG (V)',ylabel='gate I (nA)');ax[2].legend()
fig.suptitle('Raw — file 0: Gate-C scout (1D TG, BG=Si=0, B=0, sens 2mV)');plt.tight_layout();plt.show()
