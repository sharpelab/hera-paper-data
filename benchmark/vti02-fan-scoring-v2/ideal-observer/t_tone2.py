import sys, pickle, time
import numpy as np
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
labs = sys.argv[1:] or ['live 0822-r8', 'live 0825-r8', 'live 0821-r8', 'live 0824-r4', 'opus-corpus/20260923T013750-rkg9dn', 'fable-corpus/20260922T163113', 'sol-corpus/20260923T013751-g3iq70']
for lab in labs:
    d = dict(D[lab]); sel = (d['n'] >= C.N_LO) & (d['n'] <= C.N_HI); n = d['n'][sel]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d); I = d['I']
    RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    var = C.noise_var(d, Brc, RB, n)
    for M, Qe, l2 in [(3, 1, False), (3, 1, True), (2, 1, False), (4, 2, False)]:
        tones = C.hb_tones(n, {}, light2=l2)
        kl, pat, cr = C.tone_kl(muB, muR, var, Brc, n, tones, w, M=M, Qe=Qe, clutter=False)
        c = {sa: C.capped_kl(pat, kl, sa) for sa in (0.5, 1.0, 2.0)}
        print(f"{lab[:30]:30s} r{Brc.shape[0]:3d} c{n.size:3d} M{M} Q{Qe} L2{int(l2)}: KL {kl.sum():9.1f} med {np.median(kl):7.2f} ncol>1 {(kl>1).sum():3d} | cap .5 {c[0.5][0]:6.1f} 1 {c[1.0][0]:6.1f} 2 {c[2.0][0]:6.2f} n_eff {c[1.0][1]:5.1f}  h {d['h']:.2f} cells {d['cells075']:.2f}")
