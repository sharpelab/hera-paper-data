# Verbatim from Aaron's wiki page "S1 field-resolution scorer"
# https://wiki.sharpelab.science/doc/s1-field-resolution-scorer-zJo0GHFcMb
# (page updated 2026-09-13T21:01Z; copied 2026-09-13).  Local deviations: margin default 1.2 -> 1.0 (2026-09-15, agreed
# with Aaron); `strict` kwarg (2026-09-16): with b_min set, an under-sampled interval inside the window is a
# sampling_fail -- no trimming.  Default off keeps the wiki behaviour.
"""Binary field-resolution check for an SdH scan: spot check or full fan.

Per column n (the fan's density range IS the claim range):
  1. F(n) = margin * (h / g e) |n|, the fastest expected tone with a
     density-calibration margin.
  2. Walk the actual B grid in 1/B.  rows_per_period_i = (1/F) / (1/B_i - 1/B_{i+1}).
     The usable record starts after the last interval with < m rows per period
     (and at or above b_min).  Aliased low-B rows are trimmed, not fatal.
  3. Periods left in the usable record: P = F * (1/B_start - 1/B_max).
     Column passes if P >= p_min.
  A column that fails p_min even untrimmed is record-limited (low n, short
  record) -- reported, but excluded from the denominator, because that is
  record length, not sampling density.

Fan binary: passes / (passes + sampling_failures) >= f.
A spot check is a one-column fan.

delta_F per column is computed and reported, never folded into the binary.
"""
from __future__ import annotations

import numpy as np

H_OVER_E_T_M2 = 4.135667696e-15  # h/e in T*m^2
CM2_PER_M2 = 1e4

PASS, SAMPLING_FAIL, RECORD_LIMITED = "pass", "sampling_fail", "record_limited"


def luttinger_frequency(n_cm2, g: int = 4):
    """F = (h / g e) * |n|, n in cm^-2, F in T.  g = 4 -> 10.3 T per 1e12 cm^-2."""
    return H_OVER_E_T_M2 / g * np.abs(n_cm2) * CM2_PER_M2


def materialize(field, kind: str = "B") -> np.ndarray:
    """Positive B values (T), sorted ascending, deduplicated.

    field: explicit array (B or 1/B per `kind`) or a spec (lo, hi, N) uniform in `kind`.
    """
    if isinstance(field, tuple) and len(field) == 3:
        lo, hi, N = field
        grid = np.linspace(lo, hi, int(N))
    else:
        grid = np.asarray(field, dtype=float).ravel()
    if kind == "invB":
        grid = grid[grid > 0]
        B = 1.0 / grid
    elif kind == "B":
        B = grid
    else:
        raise ValueError("kind must be 'B' or 'invB'")
    B = B[np.isfinite(B) & (B > 0)]
    return np.unique(B)


def _columns(n_cm2) -> np.ndarray:
    """Density columns: scalar, array, or spec (lo, hi, N)."""
    if isinstance(n_cm2, tuple) and len(n_cm2) == 3:
        lo, hi, N = n_cm2
        return np.linspace(lo, hi, int(N))
    return np.atleast_1d(np.asarray(n_cm2, dtype=float)).ravel()


def _column_check(B: np.ndarray, F: float, *, m: float, p_min: float, strict: bool = False):
    """One column.  B sorted ascending, already cut at b_min.  Returns a dict.

    strict: any under-sampled interval in the window fails the column (the window IS the claim);
    otherwise aliased low-B rows are trimmed and the record judged from the first clean row."""
    B_max = B[-1]
    if F <= 0 or B.size < 2:
        return dict(F_T=F, B_start_T=np.nan, B_ok_T=np.nan, P_full=0.0, P=0.0,
                    delta_F_T=np.inf, rows_min=np.nan, status=RECORD_LIMITED)
    invB = 1.0 / B                       # descending
    d_invB = -np.diff(invB)              # one per interval, positive
    rows = (1.0 / F) / d_invB
    bad = np.flatnonzero(rows < m * (1 - 1e-9))   # tolerance: a grid sized exactly at m passes
    # usable record starts after the last under-sampled interval
    i_start = bad[-1] + 1 if bad.size else 0
    P_full = F * (invB[0] - invB[-1])
    if i_start >= B.size - 1:            # no interval survives
        B_start, P = np.nan, 0.0
    else:
        B_start = B[i_start]
        P = F * (1.0 / B_start - 1.0 / B_max)
    if P_full < p_min:
        status = RECORD_LIMITED
    elif strict and bad.size:
        status = SAMPLING_FAIL
    elif P < p_min:
        status = SAMPLING_FAIL
    else:
        status = PASS
    return dict(F_T=F, B_start_T=B_start,
                B_ok_T=B[bad[-1] + 1] if bad.size else B[0],   # first adequately sampled row
                P_full=P_full, P=P,
                delta_F_T=(1.0 / (1.0 / B_start - 1.0 / B_max)) if P > 0 else np.inf,
                rows_min=float(rows.min()), status=status)


def field_resolution_ok(
    field,
    n_cm2,
    *,
    kind: str = "B",
    b_min: float | None = None,
    g: int = 4,
    margin: float = 1.0,
    m: float = 3.0,
    p_min: float = 5.0,
    f: float = 0.8,
    strict: bool = False,
) -> tuple[bool, dict]:
    """Binary acceptable/unacceptable field resolution for a spot check or fan.

    field   : B or 1/B values (array) or spec (lo, hi, N) uniform in `kind`.
    n_cm2   : density columns in cm^-2 -- scalar (spot check), array, or spec (lo, hi, N).
    kind    : 'B' or 'invB'.
    b_min   : low edge of the analysis window (measured onset); rows below are dropped.
    g       : LL degeneracy (4 for the stacking tasks).
    margin  : safety factor on F_L for the density calibration (1.0; was 1.2 -- relaxed 2026-09-15 with Aaron so the recipe's Nyquist floor and this grader agree; m stays 3).
    m       : required rows per SdH period in the usable record (3).
    p_min   : minimum periods the usable record must hold (5).
    f       : fraction of resolvable columns that must pass (0.8).
    strict  : no trimming -- every interval at or above b_min must hold m rows per period.
              Use with b_min from the device's measured onset; the window is then the claim.
    """
    B = materialize(field, kind)
    if b_min is not None:
        B = B[B >= b_min]
    n = _columns(n_cm2)
    F = luttinger_frequency(n, g) * margin

    cols = [_column_check(B, float(Fi), m=m, p_min=p_min, strict=strict) for Fi in F]
    status = np.array([c["status"] for c in cols])
    n_pass = int((status == PASS).sum())
    n_samp = int((status == SAMPLING_FAIL).sum())
    n_rec = int((status == RECORD_LIMITED).sum())
    denom = n_pass + n_samp
    frac = n_pass / denom if denom else 0.0
    ok = bool(denom > 0 and frac >= f)

    diag = {
        "ok": ok,
        "pass_fraction": frac,
        "n_columns": int(n.size),
        "n_pass": n_pass,
        "n_sampling_fail": n_samp,
        "n_record_limited": n_rec,
        "reason": None if denom else "no resolvable columns in this record",
        "thresholds": dict(g=g, margin=margin, m=m, p_min=p_min, f=f, b_min=b_min, strict=strict),
        "B_window_T": (float(B[0]), float(B[-1])) if B.size else None,
        "n_rows": int(B.size),
        "columns": {
            "n_cm2": n,
            "F_T": F,
            "status": status,
            "B_ok_T": np.array([c["B_ok_T"] for c in cols]),        # first adequately sampled row
            "B_start_T": np.array([c["B_start_T"] for c in cols]),  # usable record start
            "rows_per_period_min": np.array([c["rows_min"] for c in cols]),
            "periods_full": np.array([c["P_full"] for c in cols]),
            "periods_usable": np.array([c["P"] for c in cols]),
            "delta_F_T": np.array([c["delta_F_T"] for c in cols]),
        },
    }
    return ok, diag


def _report(label, ok, d):
    c = d["columns"]
    print(f"{label}: ok={ok}  pass={d['pass_fraction']:.2f}  "
          f"(pass {d['n_pass']}, sampling-fail {d['n_sampling_fail']}, "
          f"record-limited {d['n_record_limited']}) rows={d['n_rows']}")
    if d["n_sampling_fail"]:
        i = np.flatnonzero(c["status"] == SAMPLING_FAIL)
        print(f"    sampling fails for |n| in [{abs(c['n_cm2'][i[0]]):.1e}, {abs(c['n_cm2'][i[-1]]):.1e}]; "
              f"at the top column B_ok = {c['B_ok_T'][i[-1]]:.2f} T, periods left {c['periods_usable'][i[-1]]:.1f}")


if __name__ == "__main__":
    # recipe burn: uniform-B fan, dB = 0.1 T, 0.6 -> 5 T, columns 0 -> 1e13
    ok, d = field_resolution_ok((0.6, 5.0, 45), (0, 1e13, 101), kind="B", b_min=0.6)
    _report("uniform-B dB=0.1, 0.6-5 T, n 0-1e13", ok, d)

    # same fan but B to 12 T: trimming the aliased low-B rows leaves enough record
    ok, d = field_resolution_ok((0.6, 12.0, 115), (0, 1e13, 101), kind="B", b_min=0.6)
    _report("uniform-B dB=0.1, 0.6-12 T, n 0-1e13", ok, d)

    # uniform in 1/B sized at m=3 for n_max = 1e13 (with the margin)
    Fmax = 1.2 * luttinger_frequency(1e13)
    grid = np.arange(1 / 5.0, 1 / 0.6, 1 / (3 * Fmax))
    ok, d = field_resolution_ok(grid, (0, 1e13, 101), kind="invB")
    _report(f"uniform-1/B sized for 1e13 ({grid.size} rows), 0.6-5 T", ok, d)

    # same 1/B grid inherited by a fan pushed to 2e13 without resizing
    ok, d = field_resolution_ok(grid, (0, 2e13, 101), kind="invB")
    _report("same 1/B grid, n 0-2e13", ok, d)

    # spot check: one column
    ok, d = field_resolution_ok(grid, 4e12, kind="invB")
    _report("spot check n=4e12 on that grid", ok, d)
