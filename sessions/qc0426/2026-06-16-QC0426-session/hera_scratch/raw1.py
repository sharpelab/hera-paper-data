m=load_meta(1);ci={c:i for i,c in enumerate(m['columns'])};d=load1d(1)
nf=101;nr=d.shape[0]//nf;g=d[:nr*nf].reshape(nr,nf,-1);bg=g[:,0,ci['k_bg_volt']];tg=g[0,:,ci['DC_bias']];Ib=5e-9
fig,ax=plt.subplots(1,3,figsize=(16,4.5))
for k,(nm,c) in enumerate([('sr1 Rxx','sr1_X'),('sr2 Rxx','sr2_X')]):
    R=np.abs(g[:,:,ci[c]])/Ib;im=ax[k].pcolormesh(bg,tg,R.T,shading='auto',cmap='viridis',vmax=np.percentile(R,98))
    fig.colorbar(im,ax=ax[k],label='ohm');ax[k].set(xlabel='BG(V)',ylabel='TG(V)',title=nm)
I=g[:,:,ci['sr0_X']]/m['measurement_config']['sr0_gain'];im=ax[2].pcolormesh(bg,tg,(I*1e9).T,shading='auto',cmap='inferno')
fig.colorbar(im,ax=ax[2],label='I (nA)');ax[2].set(xlabel='BG(V)',ylabel='TG(V)',title='drain I')
fig.suptitle('Raw — file 1: 0T gatemap (Si=0, sens 2mV)');plt.tight_layout();plt.show()
