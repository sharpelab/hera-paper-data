"""Span validation: how much of H_B - H_R survives the ABCA span (M harmonics, envelope degree Qe), and how much of
an ABCA-with-other-nuisance map (T_e, widths, mass) the span fails to absorb (should be ~0)."""
import sys, pickle, time
import numpy as np
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
labs = sys.argv[1:] or ['live 0822-r8', 'live 0825-r8']
for lab in labs:
    d = dict(D[lab]); sel = (d['n'] >= C.N_LO) & (d['n'] <= C.N_HI); n = d['n'][sel]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d)
    t0 = time.time()
    RB = C.clean_map(Brc, n, 'B', {}); tB = time.time() - t0
    RR = C.clean_map(Brc, n, 'R', {}); tR = time.time() - t0 - tB
    RR6 = C.clean_map(Brc, n, 'R', dict(T_K=6.0)); RR3 = C.clean_map(Brc, n, 'R', dict(T_K=3.0))
    RRw = C.clean_map(Brc, n, 'R', dict(wscale=2.0))
    I = d['I']
    muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    var = C.noise_var(d, Brc, RB, n)
    print(f"== {lab}: rows {Brc.shape[0]} cols {n.size}  clean B {tB:.1f}s R {tR:.1f}s  w {np.round(w[:4],3)}  sigma med {np.sqrt(np.median(var))*1e9:.1f} nV")
    for M, Qe in [(0, 0), (1, 1), (2, 2), (4, 2), (6, 2), (4, 3), (6, 4)]:
        kl = C.kl_columns(muB - muR, var, Brc, n, w, M=M, Qe=Qe)
        v6 = C.kl_columns(C.blur((RR6 - RR) * I, w), var, Brc, n, w, M=M, Qe=Qe).sum()
        v3 = C.kl_columns(C.blur((RR3 - RR) * I, w), var, Brc, n, w, M=M, Qe=Qe).sum()
        vw = C.kl_columns(C.blur((RRw - RR) * I, w), var, Brc, n, w, M=M, Qe=Qe).sum()
        print(f"M {M} Qe {Qe}: KL(H_B|span) total {kl.sum():10.1f}  med/col {np.median(kl):8.2f} | ABCA leak T6 {v6:8.2f} T3 {v3:8.2f} w2 {vw:8.2f}")
