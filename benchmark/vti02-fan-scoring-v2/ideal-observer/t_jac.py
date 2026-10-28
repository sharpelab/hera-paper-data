"""ABCA span + per-column ABCA nuisance directions (finite differences of the ABCA forward model): leak test and KL."""
import sys, pickle, time
import numpy as np
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
labs = sys.argv[1:] or ['live 0822-r8', 'live 0825-r8', 'live 0821-r8', 'live 0824-r4']
JAC = {'T+': dict(T_K=5.9), 'w+': dict(wscale=1.5), 'm+': dict(mscale=1.2), 'res': dict(p=dict(res_dos=0.13)),
       'hq': dict(p=dict(hq_a=2.0)), 'dn': dict(p=dict(delta_n=0.025))}
TEST = {'T3': dict(T_K=3.0), 'T6': dict(T_K=6.0), 'w2': dict(wscale=2.0), 'w.5': dict(wscale=0.5), 'm.8': dict(mscale=0.8), 'mix': dict(T_K=4.0, wscale=1.4, mscale=1.1)}
for lab in labs:
    d = dict(D[lab]); sel = (d['n'] >= C.N_LO) & (d['n'] <= C.N_HI); n = d['n'][sel]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d); I = d['I']
    t0 = time.time()
    RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    Jm = {k: C.clean_map(Brc, n, 'R', v) for k, v in JAC.items()}
    Tm = {k: C.clean_map(Brc, n, 'R', v) for k, v in TEST.items()}
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    J = [C.blur((Jm[k] - RR) * I, w) for k in JAC]
    var = C.noise_var(d, Brc, RB, n)
    print(f"== {lab} rows {Brc.shape[0]} cols {n.size} ({time.time()-t0:.0f}s)")
    for M, Qe, useJ in [(2, 1, False), (2, 1, True), (4, 1, True), (4, 2, True), (6, 2, True)]:
        JJ = J if useJ else None
        kl, res, dof = C.kl_columns(muB - muR, var, Brc, n, w, M=M, Qe=Qe, J=JJ, return_resid=True)
        leak = {k: C.kl_columns(C.blur((v - RR) * I, w), var, Brc, n, w, M=M, Qe=Qe, J=JJ).sum() for k, v in Tm.items()}
        cap = C.capped_kl(res, kl, 1.0)
        print(f"M{M} Q{Qe} J{int(useJ)} dof {dof.max():3d}: KL {kl.sum():10.1f} (med/col {np.median(kl):8.2f}) cap1 {cap[0]:6.1f} n_eff {cap[1]:5.1f} | leak " +
              ' '.join(f"{k} {v:8.1f}" for k, v in leak.items()))
