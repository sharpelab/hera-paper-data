import sys, pickle, time
import numpy as np
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
labs = sys.argv[1:] or ['live 0822-r8', 'live 0825-r8', 'live 0821-r8', 'live 0824-r4', 'opus-corpus/20260923T013750-rkg9dn', 'fable-corpus/20260922T163113', 'sol-corpus/20260923T013751-g3iq70', 'fable-corpus/20260922T232408', 'opus-none/20260923T013750-ou2xbh']
for lab in labs:
    d = dict(D[lab]); sel = (d['n'] >= C.N_LO) & (d['n'] <= C.N_HI); n = d['n'][sel]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d); I = d['I']
    RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    RR6 = C.clean_map(Brc, n, 'R', dict(wscale=0.5, T_K=3.5))
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    var = C.noise_var(d, Brc, RB, n)
    tones = C.hb_tones(n, {})
    fl = np.array([tt[0][0] if tt else 0.0 for tt in tones])
    for M, Qe in [(3, 1), (4, 2)]:
        kl, pat, _ = C.tone_kl(muB, muR, var, Brc, n, tones, w, M=M, Qe=Qe, clutter=False)
        klL, patL, _ = C.tone_kl(C.blur(RR6 * I, w), muR, var, Brc, n, tones, w, M=M, Qe=Qe, clutter=False)
        We = C.w_eff(pat, Brc)
        W = 1 / Brc.min() - 1 / Brc.max()
        ev = {sa: C.evidence(kl, fl, We, sa) for sa in (0.5, 0.7, 1.0)}
        print(f"{lab[:30]:30s} r{Brc.shape[0]:3d} c{n.size:3d} M{M}Q{Qe}: KL {kl.sum():9.0f} leakKL {klL.sum():8.1f} (ratio med {np.median(klL/np.maximum(kl,1e-9)):.3f}) W {W:.2f} Weff med {np.median(We[kl>0]) if (kl>0).any() else 0:.2f} | "
              f"nats .5 {ev[0.5][0]:6.1f} .7 {ev[0.7][0]:6.1f} 1 {ev[1.0][0]:6.2f} cells {ev[1.0][1]:5.1f} act {ev[1.0][2]:3d} | h {d['h']:.2f} cells075 {d['cells075']:.2f}")
