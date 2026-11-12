#!/usr/bin/env python3
"""
Overlay the paper-faithful ABA-TLG crossing model on QC0426 run-80 Rxx(n,B).

Run 80 = the annotated Landau fan, D = +0.25 V/nm, B 8->0 T, 161 x 201.
Steps:
  1. Re-form Rxx(n, B) from data.tsv.gz (sr1 channel) with the capacitance lever
     arm from the device card.
  2. Digitize Qingrui's 5 green dark-arc traces from the annotated PNG using the
     detected axis calibration.
  3. Compute the model ML x BL crossing loci (and N_M=0 vertical chain) across
     the data window.
  4. Optional global density-scale fit alpha: n_model -> alpha * n_model, fit to
     minimize distance to the green traces (capacitance / lever-arm uncertainty).
  5. Render overlays.

Run: uv run --no-project --with numpy --with scipy --with matplotlib --with pillow \
        python3 compare_qc0426.py
"""
from __future__ import annotations

import json
import os

import numpy as np
import scipy.constants as cst
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# ll_spectrum moved to hera/models/trilayer_fs_count (2026-07-16); make it importable
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "..", "..", "models", "trilayer_fs_count"))
from ll_spectrum import SWMcC
from crossing_model import ml_trajectories, dos_at_fermi, bright_dark_loci

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)
SRC = "/home/zack/sharpelab/dgglab-measurements/vti/qingrui/20260601-QC0426-3LGr/data"
ANNOT = "/home/zack/sharpelab/measurement-env/.worktrees/paper-faithful-detector/hera/docs/vti/refs/qc0426-fan-annotated.png"

eps0 = cst.epsilon_0
e = cst.e
kappa_hBN = 3.0
t_bg = 12e-9
t_tg = 1.3 * t_bg
c_tg = eps0 * kappa_hBN / t_tg
c_bg = eps0 * kappa_hBN / t_bg     # t_bgSiO2 = 0 -> eps0*kappa/t_bg

# Annotated-PNG axis calibration (detected from frame spines).
PX = dict(x0=116, x1=834, y0=713, ytop=45, n0=-0.6377, n1=7.8644, B0=0.0, B1=8.0)


def load_run(rid):
    m = json.load(open(f"{SRC}/{rid}/metadata.json"))
    f = f"{SRC}/{rid}/data.tsv.gz"
    arr = np.loadtxt(f)
    cols = m["columns"]
    d = {c: arr[:, i] for i, c in enumerate(cols)}
    return d, m


def fan_Rxx(rid=80, ch=1):
    d, m = load_run(rid)
    nf = len(m["fast_setpoints"][0])
    Vtg = np.asarray(m["fast_setpoints"][0])
    Vbg = np.asarray(m["fast_setpoints"][1])
    n12 = (c_tg * Vtg + c_bg * Vbg) / e * 1e-16
    B = np.asarray(m["slow_setpoints"][0])
    I = d["sr0_X"] / m["measurement_config"]["sr0_gain"]
    R = d[f"sr{ch}_X"] / I
    ns_have = R.size // nf
    B = B[:ns_have]
    R2 = R[: ns_have * nf].reshape(ns_have, nf)
    return n12, B, R2


def digitize_green(min_size=200):
    """Return list of (n12, B) arrays, one per detected green trace.

    Restricts to the plot interior and excludes the upper-left legend box so the
    legend's lime swatch is not mistaken for a trace.
    """
    from PIL import Image
    im = np.asarray(Image.open(ANNOT).convert("RGB")).astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    green = (G > 120) & (R < 110) & (B < 110) & (G - R > 40) & (G - B > 40)
    # restrict to plot interior
    mask = np.zeros_like(green)
    mask[PX["ytop"] + 2:PX["y0"] - 1, PX["x0"] + 2:PX["x1"] - 1] = True
    green &= mask
    lbl, nlab = ndimage.label(green)
    traces = []
    for k in range(1, nlab + 1):
        ys, xs = np.where(lbl == k)
        if xs.size < min_size:
            continue
        # column-median to thin the trace (one B per pixel column)
        n = PX["n0"] + (xs - PX["x0"]) / (PX["x1"] - PX["x0"]) * (PX["n1"] - PX["n0"])
        Bv = PX["B0"] + (PX["y0"] - ys) / (PX["y0"] - PX["ytop"]) * (PX["B1"] - PX["B0"])
        order = np.argsort(Bv)
        n, Bv = n[order], Bv[order]
        # reject colormap-green blobs hugging the CNP (real arcs reach n>1.5)
        if n.max() < 1.0:
            continue
        traces.append((n, Bv))
    traces.sort(key=lambda t: np.median(t[0]))
    return traces


def traj_points(traj):
    """Flatten {N_M:(n,B)} trajectories to (n_arr, B_arr)."""
    ns, bs = [], []
    for nn, bb in traj.values():
        ns.append(nn); bs.append(bb)
    return np.concatenate(ns), np.concatenate(bs)


def fit_alpha(traj, traces):
    """Global density scale alpha minimizing nearest-neighbor distance from
    each green-trace point to the scaled model trajectories (in n at matched B)."""
    Ln, LB = traj_points(traj)
    gp_n, gp_B = [], []
    for n, B in traces:
        gp_n.append(n); gp_B.append(B)
    gp_n = np.concatenate(gp_n); gp_B = np.concatenate(gp_B)

    def cost(alpha):
        tot = 0.0
        for n, B in zip(gp_n, gp_B):
            # model loci near this B
            sel = np.abs(LB - B) < 0.3
            if not sel.any():
                continue
            d = np.min(np.abs(alpha * Ln[sel] - n))
            tot += d ** 2
        return tot

    alphas = np.linspace(0.5, 2.0, 151)
    costs = [cost(a) for a in alphas]
    i = int(np.argmin(costs))
    return float(alphas[i]), float(costs[i])


_NM_COLORS = {0: "magenta", 1: "red", 2: "orange", 3: "deepskyblue", 4: "white"}


def plot_overlay(alpha=1.0, tag="", traj=None, traces=None):
    n12, B, R2 = fan_Rxx(80, ch=1)
    traj = traj if traj is not None else ml_trajectories(SWMcC(), np.linspace(0.3, 8, 120))
    traces = traces if traces is not None else digitize_green()

    fig, ax = plt.subplots(figsize=(8, 6))
    Rpos = np.clip(np.abs(R2), 30, 2e5)
    pm = ax.pcolormesh(n12, B, Rpos, cmap="viridis",
                       norm=LogNorm(vmin=50, vmax=1.5e5), shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")

    for nm, (nn, bb) in sorted(traj.items()):
        order = np.argsort(bb)
        ax.plot(alpha * nn[order], bb[order], "-", lw=2.0,
                color=_NM_COLORS.get(nm, "gray"), label=f"model $N_M$={nm}")

    for i, (n, Bv) in enumerate(traces):
        ax.plot(n, Bv, color="lime", lw=2.2, alpha=0.85,
                label="Qingrui dark arcs" if i == 0 else None)

    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.set_xlim(-0.7, 7.9); ax.set_ylim(0, 8)
    title = "QC0426 run-80 fan + ABA crossing model (level-coincidence loci)"
    if alpha != 1.0:
        title += f"  alpha={alpha:.3f}"
    ax.set_title(title, fontsize=10)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.75, ncol=2)
    fig.tight_layout()
    p = os.path.join(OUT, f"qc0426_overlay{tag}.png")
    fig.savefig(p, dpi=140); plt.close(fig); print("wrote", p)
    return p


def plot_data_only():
    n12, B, R2 = fan_Rxx(80, ch=1)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    Rpos = np.clip(np.abs(R2), 30, 2e5)
    pm = ax.pcolormesh(n12, B, Rpos, cmap="viridis",
                       norm=LogNorm(vmin=50, vmax=1.5e5), shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.set_xlim(-0.7, 7.9); ax.set_ylim(0, 8)
    ax.set_title("QC0426 run-80 Rxx(n,B), sr1  (my re-render)")
    fig.tight_layout()
    p = os.path.join(OUT, "qc0426_data_only.png")
    fig.savefig(p, dpi=140); plt.close(fig); print("wrote", p)
    return p


def plot_data_vs_dos(alpha=1.0, traces=None, nmax=150, broaden_meV=1.0):
    """Paper-style Fig 2a (measured) vs Fig 2b (calculated DOS) side by side,
    same (n, B) window, green arcs on both. Truncation corner is masked."""
    from crossing_model import dos_map, SPIN_DEG, deg_per_area, n12_from_density
    traces = traces if traces is not None else digitize_green()
    n12d, Bd, R2 = fan_Rxx(80, ch=1)

    n12g = np.linspace(-0.7, 7.9, 360)
    Bg = np.linspace(0.3, 8.0, 150)
    dos = dos_map(SWMcC(), n12g / alpha, Bg, nmax=nmax, broaden_meV=broaden_meV)
    # mask the LL-ladder truncation corner: max reachable density at each B
    for j, B in enumerate(Bg):
        nmax_reach = n12_from_density(SPIN_DEG * deg_per_area(B) * 2 * (nmax - 6))
        dos[j, (n12g / alpha) > nmax_reach] = np.nan

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), sharex=True, sharey=True)
    ax = axes[0]
    Rpos = np.clip(np.abs(R2), 30, 2e5)
    pm = ax.pcolormesh(n12d, Bd, Rpos, cmap="viridis",
                       norm=LogNorm(vmin=50, vmax=1.5e5), shading="auto")
    fig.colorbar(pm, ax=ax, label=r"$R_{xx}$ ($\Omega$)")
    for i, (n, Bv) in enumerate(traces):
        ax.plot(n, Bv, color="lime", lw=2.0, alpha=0.85,
                label="Qingrui dark arcs" if i == 0 else None)
    ax.set_title("(a) measured  QC0426 run-80  $R_{xx}(n,B)$", fontsize=10)
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.7)

    ax = axes[1]
    pm = ax.pcolormesh(n12g, Bg, dos, cmap="magma", shading="auto")
    fig.colorbar(pm, ax=ax, label="calc. DOS (arb.)")
    for n, Bv in traces:
        ax.plot(n, Bv, color="lime", lw=2.0, alpha=0.7)
    ttl = "(b) calculated DOS(n,B), ABA D=0 model"
    if alpha != 1.0:
        ttl += f"  alpha={alpha:.3f}"
    ax.set_title(ttl, fontsize=10)
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)")
    ax.set_xlim(-0.7, 7.9); ax.set_ylim(0, 8)
    fig.tight_layout()
    p = os.path.join(OUT, f"qc0426_data_vs_dos_a{alpha:.2f}.png".replace(".", "p", 1))
    fig.savefig(p, dpi=140); plt.close(fig); print("wrote", p)
    return p


def build_dos_map(cache, n12_grid, B_grid, nmax=150, broaden_meV=1.2):
    if cache and os.path.exists(cache):
        z = np.load(cache)
        return z["dos"], z["n12"], z["B"]
    dos = dos_at_fermi(SWMcC(), n12_grid, B_grid, nmax=nmax, broaden_meV=broaden_meV)
    if cache:
        np.savez(cache, dos=dos, n12=n12_grid, B=B_grid)
    return dos, n12_grid, B_grid


def _match_residual(loci, traces, alpha):
    """Median |Δn| from each green-arc point to the nearest scaled model locus
    at matched B (within 0.25 T)."""
    if not loci:
        return np.inf
    Ln = alpha * np.array([d[0] for d in loci])
    LB = np.array([d[1] for d in loci])
    res = []
    for n, B in traces:
        for nn, bb in zip(n, B):
            sel = np.abs(LB - bb) < 0.25
            if sel.any():
                res.append(np.min(np.abs(Ln[sel] - nn)))
    return float(np.median(res)) if res else np.inf


def dark_bright_test(traces=None):
    """Decisive test: do the measured dark arcs track the model's DARK
    (gap-coincidence) loci or its BRIGHT (level-coincidence) loci? Fit a global
    density scale alpha to each family and compare residuals."""
    traces = traces if traces is not None else digitize_green()
    n12_grid = np.linspace(-0.7, 7.9, 500)
    B_grid = np.linspace(0.3, 8.0, 150)
    dos, n12_grid, B_grid = build_dos_map(os.path.join(OUT, "dosEF_cache.npz"),
                                          n12_grid, B_grid)
    bright, dark = bright_dark_loci(dos, n12_grid, B_grid, prominence_frac=0.10)
    print(f"extracted {len(bright)} bright + {len(dark)} dark loci points")

    alphas = np.linspace(0.6, 1.4, 81)
    rb = [_match_residual(bright, traces, a) for a in alphas]
    rd = [_match_residual(dark, traces, a) for a in alphas]
    ib, idk = int(np.argmin(rb)), int(np.argmin(rd))
    print(f"  BRIGHT (level-coincidence): best alpha={alphas[ib]:.3f}  median|Δn|={rb[ib]:.3f}e12")
    print(f"  DARK   (gap-coincidence):   best alpha={alphas[idk]:.3f}  median|Δn|={rd[idk]:.3f}e12")

    # overlay figure at alpha=1: data + dark(cyan) + bright(red) loci + green arcs
    n12d, Bd, R2 = fan_Rxx(80, ch=1)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), sharex=True, sharey=True)
    for ax, (loci, name, col) in zip(axes, [(dark, "DARK gap-coincidence", "cyan"),
                                            (bright, "BRIGHT level-coincidence", "red")]):
        Rpos = np.clip(np.abs(R2), 30, 2e5)
        ax.pcolormesh(n12d, Bd, Rpos, cmap="viridis",
                      norm=LogNorm(vmin=50, vmax=1.5e5), shading="auto")
        if loci:
            xs = [d[0] for d in loci]; ys = [d[1] for d in loci]
            ax.scatter(xs, ys, s=6, c=col, alpha=0.6, label=f"model {name} loci")
        for i, (n, Bv) in enumerate(traces):
            ax.plot(n, Bv, color="lime", lw=2.0, alpha=0.85,
                    label="Qingrui dark arcs" if i == 0 else None)
        ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)")
        ax.set_xlim(-0.7, 7.9); ax.set_ylim(0, 8)
        ax.set_title(f"data + model {name} loci ($\\alpha$=1)", fontsize=10)
        ax.legend(loc="upper left", fontsize=8, framealpha=0.7)
    axes[0].set_ylabel("B (T)")
    fig.tight_layout()
    p = os.path.join(OUT, "qc0426_dark_vs_bright.png")
    fig.savefig(p, dpi=140); plt.close(fig); print("wrote", p)

    # model DOS(E_F) map with green arcs (the "calculated dark fan")
    fig, ax = plt.subplots(figsize=(7.5, 5.6))
    pm = ax.pcolormesh(n12_grid, B_grid, dos, cmap="magma", shading="auto")
    fig.colorbar(pm, ax=ax, label=r"calc. DOS$(E_F)$ (compressibility)")
    for n, Bv in traces:
        ax.plot(n, Bv, color="lime", lw=2.0, alpha=0.8)
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.set_xlim(-0.7, 7.9); ax.set_ylim(0, 8)
    ax.set_title("model DOS$(E_F)$(n,B): dark=incompressible, bright=compressible", fontsize=10)
    fig.tight_layout()
    p2 = os.path.join(OUT, "qc0426_dosEF_map.png")
    fig.savefig(p2, dpi=140); plt.close(fig); print("wrote", p2)
    return dict(alpha_bright=float(alphas[ib]), res_bright=float(rb[ib]),
                alpha_dark=float(alphas[idk]), res_dark=float(rd[idk]))


def plot_cuts_across(alpha=0.82, traj=None, traces=None):
    """Show the arcs cut ACROSS constant-nu rays (the crossing-chain signature),
    not along them (the straight-ray misread). Dashed lines = constant filling
    factor nu; green = arcs; colored = model ML crossing chains."""
    import scipy.constants as cst
    traj = traj if traj is not None else load_traj(os.path.join(OUT, "traj_cache.npz"))
    traces = traces if traces is not None else digitize_green()
    n12, B, R2 = fan_Rxx(80, ch=1)
    fig, ax = plt.subplots(figsize=(8, 6))
    Rpos = np.clip(np.abs(R2), 30, 2e5)
    ax.pcolormesh(n12, B, Rpos, cmap="viridis",
                  norm=LogNorm(vmin=50, vmax=1.5e5), shading="auto")
    # constant-nu reference rays: n12 = nu * e*B/h / 1e16
    Bline = np.linspace(0.05, 8, 50)
    for nu in range(10, 160, 10):
        nline = nu * cst.e * Bline / cst.h / 1e16
        ax.plot(nline, Bline, color="0.7", lw=0.5, ls="--", alpha=0.6)
    for nm, (nn, bb) in sorted(traj.items()):
        o = np.argsort(bb)
        ax.plot(alpha * nn[o], bb[o], "-", lw=1.8, color=_NM_COLORS.get(nm, "gray"),
                label=f"model $N_M$={nm}")
    for i, (n, Bv) in enumerate(traces):
        ax.plot(n, Bv, color="lime", lw=2.4, alpha=0.9,
                label="Qingrui dark arcs" if i == 0 else None)
    ax.set_xlabel(r"$n$ ($10^{12}$ cm$^{-2}$)"); ax.set_ylabel("B (T)")
    ax.set_xlim(-0.7, 7.9); ax.set_ylim(0, 8)
    ax.set_title(r"Arcs cut ACROSS constant-$\nu$ rays (grey dashed) "
                 r"= crossing-chain signature  ($\alpha$=%.2f)" % alpha, fontsize=9)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.75, ncol=2)
    fig.tight_layout()
    p = os.path.join(OUT, "qc0426_cuts_across.png")
    fig.savefig(p, dpi=140); plt.close(fig); print("wrote", p)
    return p


def load_traj(cache):
    if cache and os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        return {int(k): tuple(z[k]) for k in z.files}
    traj = ml_trajectories(SWMcC(), np.linspace(0.3, 8.0, 150), nmax=150, nm_max=4)
    if cache:
        np.savez(cache, **{str(k): np.array(v, dtype=object) for k, v in traj.items()})
    return traj


if __name__ == "__main__":
    plot_data_only()
    traj = load_traj(os.path.join(OUT, "traj_cache.npz"))
    traces = digitize_green()
    print(f"digitized {len(traces)} green traces; trajectories N_M={sorted(traj)}")
    for t in traces:
        print(f"  trace: n {t[0].min():.2f}..{t[0].max():.2f}  B {t[1].min():.2f}..{t[1].max():.2f}")
    plot_overlay(alpha=1.0, tag="_a1", traj=traj, traces=traces)
    alpha, c = fit_alpha(traj, traces)
    print(f"best-fit density scale alpha = {alpha:.3f} (cost {c:.3f})")
    plot_overlay(alpha=alpha, tag="_afit", traj=traj, traces=traces)
    plot_data_vs_dos(alpha=1.0, traces=traces)
    plot_cuts_across(alpha=0.82, traj=traj, traces=traces)
    print("=== dark vs bright (gap- vs level-coincidence) test ===")
    res = dark_bright_test(traces=traces)
    print(res)
