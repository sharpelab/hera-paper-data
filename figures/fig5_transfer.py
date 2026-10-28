"""Fig. 5: domain transfer, HERA on the WSe2-proximitized bilayer graphene device (zf1, toploader).

(a) the timeline of session 6 (E1, unaided decisive superconductor call); (b) dV_xx/dI against dc current at
four rungs of session 6's temperature ladder (runs 13, 16, 17, 18) at the dome optimum n = -5.00e11 cm^-2,
D = -0.64 V/nm; (c) coverage: the superconducting dome from the operator-in-the-loop reference session (r7 run 3)
inside the gate window, with the cuts sessions 2 and 3 took and session 3's operating point.

Reads sessions/zf1/ and figures/data/zf1-r7/ (r7 run 3 and the matched operating points; the r7 session is not
one of HERA's archived sessions, so its one run used here lives with the figures).
Run from the repo root: uv run --project measurement-env python figures/fig5_transfer.py [outdir]
Adapted from ~/work/projects/hera/zf1/zf1_paper_figures.ipynb cells 4, 16, 19, 21 and the TikZ timeline
fig-main-timeline-zf1.tex.
"""
import json
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon
from matplotlib.ticker import MultipleLocator
from scipy.spatial import ConvexHull

import style

sys.path.insert(0, str(style.ROOT / "measurement-env/src"))
from hera.analysis import open_run, GateCalibration  # noqa: E402

style.use()
ARCH = style.ROOT / "sessions/zf1"
R7 = style.HERE / "data/zf1-r7"
SESS = {1: "2026-06-20-zf1-session", 2: "2026-06-21-zf1-session", 3: "2026-06-22-zf1-session",
        4: "2026-06-23-zf1-session-full", 5: "2026-06-24-zf1-session", 6: "2026-06-25-zf1-session"}
CAL = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=-0.362e11 * 1e4)  # session r7 n_offset
TG_LIM, BG_LIM = (-7.0, 6.0), (-4.0, 4.2)                  # gate validators, every session
NOTE = plt.rcParams["legend.fontsize"]

# (a) active hours of session 6: run starts (log.log sweep starts, rig clock PDT) as hours after the brief (22:39:03),
# less the 0.784 h to the grant of autonomy (23:26:06, transcript "go for autonomy"); E1 with no standby, so active
# time is time since the grant (Methods). The gate checks (runs 0-3) ran before the grant and are not drawn. Two
# breaks remove 3.6 h inside the gate map and 1.1 h inside the analysis before the conclusion.
GRANT = 0.784
GA, GB = 3.6, 4.70
EVENTS = [(0.81 - GRANT, "gate map"), (4.87 - GA - GRANT, "search for zero resistance"),
          (5.16 - GA - GRANT, "fine map"), (5.52 - GA - GRANT, "critical current"), (5.81 - GA - GRANT, "critical field"),
          (6.27 - GA - GRANT, "critical temperature (b)"), (7.90 - GB - GRANT, "Return conclusion")]


def rxx(run):
    I = run.col("sr830_1_X") / (-1e6)               # Ithaco gain -1e6
    return np.abs((run.col("sr830_3_X") / 100.0) / I)  # 4T 30-31, x100 preamp


def nD(vtg, vbg):
    n_m2, D_Vm = CAL.n_D(np.asarray(vtg, float), np.asarray(vbg, float))
    return n_m2 * 1e-15, D_Vm * 1e-9


def edges(c):
    c = np.asarray(c, float); e = np.empty(len(c) + 1)
    e[1:-1] = 0.5 * (c[:-1] + c[1:]); e[0] = c[0] - 0.5 * (c[1] - c[0]); e[-1] = c[-1] + 0.5 * (c[-1] - c[-2])
    return e


def dome_grid(run, dn=0.03, dD=0.0025, n_rng=(-7.0, -1.0), D_rng=(-0.69, -0.40)):
    """Bin a boustrophedon (n, D) multisweep to its planned grid. Uses the measured current for R."""
    n11, D = nD(run.col_at(run.col_indices("k_tg_volt")[0]), run.col_at(run.col_indices("k_bg_volt")[0]))
    R = rxx(run)
    n_grid = np.round(np.arange(n_rng[0], n_rng[1] + dn / 2, dn), 5)
    D_grid = np.round(np.arange(D_rng[0], D_rng[1] + dD / 2, dD), 5)
    ni = np.round((n11 - n_grid[0]) / dn).astype(int); di = np.round((D - D_grid[0]) / dD).astype(int)
    Z = np.full((len(D_grid), len(n_grid)), np.nan)
    ok = (ni >= 0) & (ni < len(n_grid)) & (di >= 0) & (di < len(D_grid))
    Z[di[ok], ni[ok]] = R[ok]
    return n_grid, D_grid, Z


def gate_sweeps(session):
    """Every gate-swept run in the session -> list of (n, D, kind), kind in survey | zoom | path | cut."""
    out = []
    for p in sorted((ARCH / SESS[session] / "data").iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else 10**9):
        if not p.name.isdigit():
            continue
        try:
            r = open_run(p)
        except Exception:
            continue
        it, ib = r.col_indices("k_tg_volt"), r.col_indices("k_bg_volt")
        if not it or not ib:
            continue
        vtg, vbg = r.col_at(it[-1]), r.col_at(ib[-1])
        if np.nanstd(vtg) < 1e-3 and np.nanstd(vbg) < 1e-3:
            continue
        if (r.recipe or "").startswith("gate-current-sanity"):        # single-gate liveness legs
            continue
        n, D = nD(vtg, vbg)
        Dspan, nspan = np.nanmax(D) - np.nanmin(D), np.nanmax(n) - np.nanmin(n)
        rows = np.unique(np.round(D[np.isfinite(D)], 3))
        if Dspan < 0.01 or len(rows) <= 8:                            # one or a few fixed-D rows: cuts
            for Dr in rows:
                m = np.abs(D - Dr) < 0.002
                if m.sum() > 5:
                    out.append((n[m], D[m], "cut"))
        else:
            ok = np.isfinite(n) & np.isfinite(D); pts = np.c_[n[ok], D[ok]]
            cells = len({(int(a), int(b)) for a, b in zip(pts[:, 0] / 0.1, pts[:, 1] / 0.005)})
            try:
                hull_cells = ConvexHull(pts).volume / (0.1 * 0.005)
            except Exception:
                hull_cells = np.inf
            out.append((n, D, "survey" if nspan > 50 else ("zoom" if cells > 0.3 * hull_cells else "path")))
    return out


def ladder(ax):
    sel = [13, 16, 17, 18]                                    # 34, 158, 230, 321 mK
    cols = plt.get_cmap("inferno")(np.linspace(0.0, 0.8, len(sel)))
    for c, rid in zip(cols, sel):
        r = open_run(ARCH / SESS[6] / "data" / str(rid))
        Idc = r.col_at(r.col_indices("dc205_1_voltage")[0]) / 100e6 * 1e9          # nA through the 100 MOhm bias resistor
        dVdI = (r.col_at(r.col_indices("sr830_3_X")[0]) / 100.0) / 0.5e-9           # Ohm: 4T voltage / AC current
        T = np.median(r.col_at(r.col_indices("T")[0])) * 1e3
        ax.plot(Idc, dVdI, lw=0.9, color=c, label=f"{T:.0f} mK")
    ax.set_xlim(-60, 60); ax.set_ylim(-5, 130)
    ax.set_yticks([0, 25, 50, 75, 100, 125])
    ax.set_xlabel(r"$I_\mathrm{dc}$ (nA)"); ax.set_ylabel(r"$\mathrm{d}V_{xx}/\mathrm{d}I$ ($\Omega$)")
    leg = ax.legend(loc="lower left", bbox_to_anchor=(-0.01, 1.01), ncol=2, columnspacing=0.7, handlelength=1.0,
                    handletextpad=0.4, borderaxespad=0.0, labelspacing=0.15)
    for h in leg.get_lines():
        h.set_linewidth(2.5)


def coverage(fig, ax):
    n_grid, D_grid, Z = dome_grid(open_run(R7 / "data/3"))
    box = [(TG_LIM[0], BG_LIM[0]), (TG_LIM[1], BG_LIM[0]), (TG_LIM[1], BG_LIM[1]), (TG_LIM[0], BG_LIM[1]),
           (TG_LIM[0], BG_LIM[0])]
    env_n, env_D = nD([b[0] for b in box], [b[1] for b in box])
    ops = {int(o["run"][1]): (o["n"], o["D"]) for o in json.loads((R7 / "matched_points.json").read_text())
           if o["run"] != "r7"}
    col = {2: "tab:orange", 3: "tab:red"}
    lw = {2: 2.6, 3: 2.0}; zo = {2: 4, 3: 5}; al = {2: 0.75, 3: 0.85}
    ax.add_patch(Polygon(np.c_[env_n, env_D], closed=True, fc="#e4e4e4", ec="none", zorder=0.5))   # the accessible gate window
    pm = ax.pcolormesh(edges(n_grid), edges(D_grid), np.ma.masked_invalid(np.clip(Z, 1.0, None)), cmap="viridis",
                       norm=mcolors.LogNorm(1.0, 1e3), shading="flat", rasterized=True, zorder=1)
    clip = Polygon(np.c_[env_n, env_D], closed=True, transform=ax.transData, fc="none", ec="none")
    ax.add_patch(clip); pm.set_clip_path(clip)                 # the dome map ends on the gate limit
    ax.grid(False)
    ax.plot(env_n, env_D, color="k", lw=1.3, ls="-", zorder=4.5)  # gate-window envelope
    dash = (0, (3, 2))
    for s in (2, 3):
        cuts = {}                                                    # repeated cuts at one D merge into one line
        for n, D, k in gate_sweeps(s):
            ok = np.isfinite(n) & np.isfinite(D)
            if k in ("survey", "zoom"):
                continue
            if k == "cut":
                key = round(float(np.nanmedian(D[ok])), 3); lo, hi = np.nanmin(n[ok]), np.nanmax(n[ok])
                cuts[key] = (min(lo, cuts[key][0]), max(hi, cuts[key][1])) if key in cuts else (lo, hi)
                continue
            x, y = n[ok], D[ok]; step = np.hypot(np.diff(x) / 10, np.diff(y) / 0.35)
            for seg in np.split(np.arange(len(x)), np.flatnonzero(step > 6 * np.median(step)) + 1):
                if len(seg) <= 3:
                    continue
                if np.ptp(y[seg]) < 0.005:                           # a fixed-D segment: merge with the cuts
                    key = round(float(np.median(y[seg])), 3); lo, hi = x[seg].min(), x[seg].max()
                    cuts[key] = (min(lo, cuts[key][0]), max(hi, cuts[key][1])) if key in cuts else (lo, hi)
                else:                                                # the edge sweep along the gate limit
                    ax.plot(x[seg], y[seg], color=col[s], lw=lw[s], alpha=al[s], ls=dash, solid_capstyle="butt",
                            zorder=zo[s])
        for Dr, (lo, hi) in cuts.items():
            ax.plot([lo, hi], [Dr, Dr], color=col[s], lw=lw[s], alpha=al[s], ls=dash, solid_capstyle="butt", zorder=zo[s])
    ax.plot(*ops[3], "o", mfc="none", mec=col[3], mew=1.0, ms=5, zorder=6)
    for s in (2, 3):
        ax.plot([], [], color=col[s], lw=lw[s], alpha=al[s], ls=dash, label=f"session {s}")
    leg = ax.legend(loc="lower left", bbox_to_anchor=(-0.01, 1.01), ncol=1, labelspacing=0.15, handlelength=1.0,
                    handletextpad=0.4, borderaxespad=0.0)
    # the colour bar fills the strip right of the legend, its label just after the legend text
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    box = ax.get_window_extent(r)
    lab = r"$R_{xx}$ ($\Omega$)"
    t = ax.text(0, 0, lab, fontsize=plt.rcParams["legend.fontsize"]); lw_px = t.get_window_extent(r).width; t.remove()
    x0 = (leg.get_window_extent(r).x1 - box.x0 + 6 / 72 * fig.dpi + lw_px + 3 / 72 * fig.dpi) / box.width
    cb = style.topbar(fig, ax, pm, lab, [1, 10, 100, 1000], x0=x0, w=1 - x0)
    cb.set_xticklabels([r"$10^0$", "", r"$10^2$", ""])
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.set_xlim(-11, 1); ax.set_ylim(-0.72, -0.40)
    ax.set_yticks([-0.7, -0.6, -0.5, -0.4])
    ax.set_xlabel(r"$n$ ($10^{11}$ cm$^{-2}$)"); ax.set_ylabel(r"$D/\epsilon_0$ (V/nm)")


def main(out):
    W, H = style.TEXT_W, 2.1
    fig = plt.figure(figsize=(W, H))
    # the old layout: a 0.36 textwidth timeline column, then two 0.30 textwidth panels whose axes were
    # 1.557 x 1.189 in (left 0.24, right 0.975, bottom 0.19, top 0.80 of a 2.118 x 1.95 in figure)
    ay, ah, aw = 0.37, 1.189, 1.557
    b = style.axes_in(fig, 3.19, ay, aw, ah)
    ladder(b)
    c = style.axes_in(fig, 5.45, ay, aw, ah)
    coverage(fig, c)
    a = style.axes_in(fig, 0.12, ay - 0.25, 2.30, 0.50)
    style.timeline(a, end=3.50 - GRANT, breaks=[1.13 - GRANT, 2.87 - GRANT],
                   ticks=[(0, "0"), (5 + GRANT - GA - GRANT, "5"), (7 + GRANT - GB - GRANT, "7")],
                   events=EVENTS, xlabel="active hours into the session")
    # centre the whole timeline, its labels through its axis label, on the plots' mid-height
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    ext = [t.get_window_extent(r) for t in a.texts if t.get_text()]
    lo, hi = min(e.y0 for e in ext) / fig.dpi, max(e.y1 for e in ext) / fig.dpi
    p = a.get_position()
    a.set_position([p.x0, p.y0 + (ay + ah / 2 - (lo + hi) / 2) / H, p.width, p.height])
    fig.canvas.draw()
    a_top = max(t.get_window_extent(r).y1 for t in a.texts if t.get_text()) / fig.dpi
    style.panel_label(fig, b, "a", y=a_top + 0.08, x=0.04)   # just above the timeline's labels, as Fig. 2a
    style.panel_label(fig, b, "b", y=a_top + 0.08)   # one baseline with (a)
    style.panel_label(fig, c, "c", y=a_top + 0.08)
    style.save(fig, out)
    plt.close(fig)


if __name__ == "__main__":
    out = style.outdir(sys.argv)
    main(out / "fig5-transfer.pdf")
    print("wrote", out / "fig5-transfer.pdf")
