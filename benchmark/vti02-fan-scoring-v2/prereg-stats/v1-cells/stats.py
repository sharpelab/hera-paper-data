"""Quality-hours dominance statistics. Points are (Q, h); larger Q and smaller h are better.
The floor point (0, inf) stands for "no fan worth anything": every floor point ties with every
other and is dominated by any point with Q > 0 and finite h."""
import numpy as np

INF = np.inf


def place(eps, qkey, policy='floor'):
    """Episodes -> (Q, h) points under a placement policy. Excluded / ungraded episodes never
    reach here.
      floor   : non-fan endings and Q = 0 fans at the floor (0, inf)            [recommended]
      own     : Q = 0 fans at (0, own hours); non-fan endings at the floor
      landed  : fans only; Q = 0 fans at the floor
    """
    pts = []
    for e in eps:
        if e['ending'] != 'fan':
            if policy == 'landed':
                continue
            pts.append((0.0, INF))
            continue
        q, h = e[qkey], e['hours']
        if q <= 0:
            pts.append((0.0, h) if policy == 'own' else (0.0, INF))
        else:
            pts.append((q, h))
    return np.array(pts, float).reshape(-1, 2)


def dom_matrix(A, B):
    """[i, j] = +1 if A_i dominates B_j, -1 if B_j dominates A_i, 0 otherwise (ties, incomparable)."""
    qa, ha = A[:, 0][:, None], A[:, 1][:, None]
    qb, hb = B[:, 0][None, :], B[:, 1][None, :]
    ab = (qa >= qb) & (ha <= hb) & ((qa > qb) | (ha < hb))
    ba = (qb >= qa) & (hb <= ha) & ((qb > qa) | (hb < ha))
    return ab.astype(float) - ba.astype(float)


def D(A, B):
    """Pairwise dominance: P(a > b) - P(b > a), a from A, b from B. In [-1, 1]."""
    if len(A) == 0 or len(B) == 0:
        return np.nan
    return float(dom_matrix(A, B).mean())


def hv_set(P, h_ref, qnorm=1.0):
    """Hypervolume of the region dominated by P inside [0, qnorm] x [0, h_ref] (area / (qnorm h_ref))."""
    P = P[(P[:, 1] < h_ref) & (P[:, 0] > 0)]
    if len(P) == 0:
        return 0.0
    P = P[np.argsort(P[:, 1])]
    area, qbest = 0.0, 0.0
    hs = np.r_[P[:, 1], h_ref]
    for i in range(len(P)):
        qbest = max(qbest, min(P[i, 0], qnorm))
        area += qbest * (hs[i + 1] - hs[i])
    return area / (qnorm * h_ref)


def hv1(P, h_ref, qnorm=1.0):
    """Per-episode hypervolume (each point's own rectangle), averaged: mean Q/qnorm x (1 - h/h_ref)+."""
    if len(P) == 0:
        return np.nan
    q = np.minimum(P[:, 0], qnorm) / qnorm
    t = np.clip(1 - P[:, 1] / h_ref, 0, 1)
    t = np.where(np.isinf(P[:, 1]), 0.0, t)
    return float((q * t).mean())


def frontier_share(A, B):
    """Share of A's and of B's points on the pooled non-dominated set (floor points never count)."""
    P = np.vstack([A, B])
    M = dom_matrix(P, P)
    nd = ~(M < 0).any(1) & np.isfinite(P[:, 1]) & (P[:, 0] > 0)
    return float(nd[:len(A)].mean()) if len(A) else np.nan, float(nd[len(A):].mean()) if len(B) else np.nan


def ref_score(P, R):
    """Per-episode reference-dominance score u_i = P(i > r) - P(r > i) against a frozen reference set R."""
    return dom_matrix(P, R).mean(1)


# ---------------------------------------------------------------- pooled estimands
def pooled(cells, stat, models):
    """Mean over models of stat(corpus cell, none cell); models lacking either arm are skipped."""
    v = [stat(cells[(m, 'corpus')], cells[(m, 'none')]) for m in models
         if len(cells.get((m, 'corpus'), [])) and len(cells.get((m, 'none'), []))]
    return float(np.mean(v)) if v else np.nan


def boot(cells, stat, models, B=2000, rng=None, alpha=0.05):
    """Stratified percentile bootstrap: episodes resampled within each (model, arm) cell."""
    rng = rng or np.random.default_rng(0)
    est = pooled(cells, stat, models)
    keys = [k for k in cells if len(cells[k])]
    vals = np.empty(B)
    for b in range(B):
        c = {k: cells[k][rng.integers(0, len(cells[k]), len(cells[k]))] for k in keys}
        vals[b] = pooled(c, stat, models)
    lo, hi = np.nanpercentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return est, lo, hi
