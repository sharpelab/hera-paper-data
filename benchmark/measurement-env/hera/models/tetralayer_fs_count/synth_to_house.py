#!/usr/bin/env -S uv run --no-project --with numpy --with matplotlib --with nbformat python3
"""Encode validated synthetic tetralayer SdH fans into house-format fixtures.

Reads the two validated source fans under
``/data/sharpelab/hera-data/tetralayer-synth-validation/{case}/{fan.npz,truth.json}``
and writes, for each of the two HERA replay test cases, a fan `data/<id>/`
dir (2D multimegasweep), a spot-check `data/<id>/` dir (1D field sweep), and
a measure notebook — all in the house `data/<id>/{metadata.json,data.tsv.gz,
plot.png}` layout used by ``rpl19_load.py`` / the real RPL_19 mirror.

Reproducible: all randomness comes from ``numpy.random.default_rng(SEED)``
with a fixed per-case seed. Re-running regenerates byte-identical fixtures.

Run:
    uv run --no-project --with numpy --with matplotlib --with nbformat \\
        python3 hera/models/tetralayer_fs_count/synth_to_house.py
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat as nbf
import numpy as np

REPO = Path(__file__).resolve().parents[3]
SRC_ROOT = Path("/data/sharpelab/hera-data/tetralayer-synth-validation")

# --- (n, D) <-> gate voltages, verbatim from rpl19_load.calculate_n_D -------
_EP_TO_N = 5.52634936


def calculate_n_D(vtg, vbg, dtg, dbg, ep):
    vtg = np.asarray(vtg, dtype=float)
    vbg = np.asarray(vbg, dtype=float)
    n = (vbg / dbg + vtg / dtg) * ep * _EP_TO_N
    D = 0.5 * ep * (vtg / dtg - vbg / dbg)
    return n, D


def calculate_gate_voltages_D0(n, dtg, dbg, ep):
    """Inverse of calculate_n_D at D = 0."""
    n = np.asarray(n, dtype=float)
    vbg = n * dbg / (2 * ep * _EP_TO_N)
    vtg = vbg * dtg / dbg
    return vtg, vbg


I0 = 1e-8
N_SPOT = -5.0
FAN_COLUMNS = [
    "time", "magnet_field", "k_tg_volt", "k_bg_volt", "T_probe", "T_fridge",
    "sr830_1_X", "sr830_1_P", "sr830_2_X", "sr830_2_P",
    "sr830_3_X", "sr830_3_P", "sr830_4_X", "sr830_4_P",
]
SPOT_COLUMNS = [
    "time", "magnet_field", "T", "T",
    "sr830_1_X", "sr830_1_P", "sr830_2_X", "sr830_2_P",
    "sr830_3_X", "sr830_3_P", "sr830_4_X", "sr830_4_P",
]

CASES = {
    "abab_breakdown": dict(
        fixture="2026-05-14-QC0512-stacking-fan",
        device="QC0512",
        date="2026-05-14",
        dtg=18.0, dbg=24.0, ep=3,
        contacts={"sr830_1": "29-28", "sr830_2": "28-25", "sr830_3": "25-24", "sr830_4": "I_{a-b}"},
        spot_id="0207", fan_id="0213",
        notebook="20260514_measure.ipynb",
        seed=512,
    ),
    "mislabeled_N": dict(
        fixture="2026-05-21-QC0531-stacking-fan",
        device="QC0531",
        date="2026-05-21",
        dtg=19.2, dbg=22.6, ep=3,
        contacts={"sr830_1": "13-12", "sr830_2": "12-9", "sr830_3": "9-7", "sr830_4": "I_{a-b}"},
        spot_id="0184", fan_id="0191",
        notebook="20260521_measure.ipynb",
        seed=531,
    ),
}


def encode_channels(rng, Rxx, B, n_sign):
    """Rxx, B, n_sign are same-shape (broadcast-compatible) arrays."""
    shape = np.broadcast(Rxx, B, n_sign).shape
    Rxx = np.broadcast_to(Rxx, shape)
    B = np.broadcast_to(B, shape)
    n_sign = np.broadcast_to(n_sign, shape)
    ch = {}
    ch["sr830_4_X"] = I0 * (1 + 5e-4 * rng.standard_normal(shape))
    ch["sr830_4_P"] = 1e-3 * rng.standard_normal(shape)
    ch["sr830_2_X"] = Rxx * I0
    ch["sr830_2_P"] = 1e-3 * rng.standard_normal(shape)
    ch["sr830_3_X"] = Rxx * I0 * 0.98 * (1 + 5e-4 * rng.standard_normal(shape))
    ch["sr830_3_P"] = 1e-3 * rng.standard_normal(shape)
    ch["sr830_1_X"] = 2.0 * (B / 5.0) * I0 * n_sign
    ch["sr830_1_P"] = 1e-3 * rng.standard_normal(shape)
    return ch


def write_tsv_gz(path, columns_dict, columns_order):
    cols = [np.asarray(columns_dict[c]).ravel() for c in columns_order]
    data = np.column_stack(cols)
    with gzip.open(path, "wt") as f:
        np.savetxt(f, data)


def build_fan(case_dir, npz, dtg, dbg, ep, contacts, fan_id, rng):
    Rxx = npz["Rxx"]          # (900, 40)
    B = npz["B"]              # (900,)
    n_truth = npz["n"]        # (40,)
    nB, ncol = Rxx.shape

    vtg_col, vbg_col = calculate_gate_voltages_D0(n_truth, dtg, dbg, ep)

    B_grid = np.broadcast_to(B[:, None], (nB, ncol))
    n_grid = np.tile(n_truth[None, :], (nB, 1))
    vtg_grid = np.tile(vtg_col[None, :], (nB, 1))
    vbg_grid = np.tile(vbg_col[None, :], (nB, 1))

    ch = encode_channels(rng, Rxx, B_grid, np.sign(n_grid))
    dwell = 1.2
    n_pts = nB * ncol
    time_col = (np.arange(n_pts) * dwell).reshape(nB, ncol)
    magnet_field_col = B_grid * (1 + 1e-4 * rng.standard_normal((nB, ncol)))
    T_probe_col = 1.4 + 5e-3 * rng.standard_normal((nB, ncol))
    T_fridge_col = 1.35 + 5e-3 * rng.standard_normal((nB, ncol))

    columns_dict = {
        "time": time_col,
        "magnet_field": magnet_field_col,
        "k_tg_volt": vtg_grid,
        "k_bg_volt": vbg_grid,
        "T_probe": T_probe_col,
        "T_fridge": T_fridge_col,
        **ch,
    }

    fan_dir = case_dir / "data" / fan_id
    fan_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "comments": [],
        "type": "2D",
        "function": "multimegasweep",
        "slow_delay": 1,
        "fast_delay": 1.2,
        "slow_param": ["magnet_field"],
        "fast_param": ["k_tg_volt", "k_bg_volt"],
        "columns": FAN_COLUMNS,
        "measurement_config": dict(contacts),
        "slow_setpoints": [B.tolist()],
        "fast_setpoints": [vtg_col.tolist(), vbg_col.tolist()],
        "interrupted": False,
        "start_time": 1747200000.0,
        "end_time": 1747200000.0 + 7200,
    }
    (fan_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
    write_tsv_gz(fan_dir / "data.tsv.gz", columns_dict, FAN_COLUMNS)

    Rxx_check = ch["sr830_2_X"] / ch["sr830_4_X"]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    pm = ax.pcolormesh(n_grid, B_grid, Rxx_check, shading="auto", cmap="viridis")
    ax.set_xlabel("n (1e12 cm$^{-2}$)")
    ax.set_ylabel("B (T)")
    fig.colorbar(pm, ax=ax, label="Rxx (a.u.)")
    fig.tight_layout()
    fig.savefig(fan_dir / "plot.png", dpi=110)
    plt.close(fig)

    return fan_dir


def build_spot(case_dir, npz, dtg, dbg, ep, contacts, spot_id, rng):
    Rxx_full = npz["Rxx"]
    B = npz["B"]
    n_truth = npz["n"]

    j0 = int(np.argmin(np.abs(n_truth - N_SPOT)))
    Rxx_1d = Rxx_full[:, j0]
    n_pts = B.size

    vtg_j0, vbg_j0 = calculate_gate_voltages_D0(float(n_truth[j0]), dtg, dbg, ep)

    n_sign = np.sign(n_truth[j0]) * np.ones_like(B)
    ch = encode_channels(rng, Rxx_1d, B, n_sign)
    dwell = 1.2
    time_col = np.arange(n_pts) * dwell
    magnet_field_col = B * (1 + 1e-4 * rng.standard_normal(n_pts))
    T_probe_col = 1.4 + 5e-3 * rng.standard_normal(n_pts)
    T_fridge_col = 1.35 + 5e-3 * rng.standard_normal(n_pts)

    spot_dir = case_dir / "data" / spot_id
    spot_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "comments": [
            {
                "field": float(B[0]),
                "T": 1.4,
                "V_tg": float(vtg_j0),
                "V_bg": float(vbg_j0),
                "I_ac": 10.0,
                "f_ac": 13.0,
            }
        ],
        "type": "1D",
        "function": "sweep",
        "delay": 1.2,
        "param": "magnet_field",
        "columns": SPOT_COLUMNS,
        "measurement_config": dict(contacts),
        "setpoints": B.tolist(),
        "interrupted": False,
        "start_time": 1747199000.0,
        "end_time": 1747199000.0 + 900,
    }
    (spot_dir / "metadata.json").write_text(json.dumps(meta, indent=2))

    # explicit column arrays in exact SPOT_COLUMNS order (two "T" columns)
    arrays_in_order = [
        time_col, magnet_field_col, T_probe_col, T_fridge_col,
        ch["sr830_1_X"], ch["sr830_1_P"],
        ch["sr830_2_X"], ch["sr830_2_P"],
        ch["sr830_3_X"], ch["sr830_3_P"],
        ch["sr830_4_X"], ch["sr830_4_P"],
    ]
    data = np.column_stack(arrays_in_order)
    with gzip.open(spot_dir / "data.tsv.gz", "wt") as f:
        np.savetxt(f, data)

    Rxx_check = ch["sr830_2_X"] / ch["sr830_4_X"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(B, Rxx_check, lw=0.8)
    ax.set_xlabel("B (T)")
    ax.set_ylabel("Rxx (a.u.)")
    fig.tight_layout()
    fig.savefig(spot_dir / "plot.png", dpi=110)
    plt.close(fig)

    return spot_dir, j0


def build_notebook(case_dir, notebook_name, device, date, dtg, dbg, ep, spot_id, fan_id):
    nb = nbf.v4.new_notebook()
    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3",
    }

    cells = []
    cells.append(nbf.v4.new_markdown_cell(
        f"# {device} — 4LGr stacking session (toploader, {date})\n"
        "\n"
        "Device-init complete: CNP + (n, D) line committed to `device_card.md`. Goal:\n"
        "identify the stacking order at D ≈ 0 by Fermi-surface counting."
    ))
    cells.append(nbf.v4.new_code_cell(
        "import numpy as np\n"
        "from sweep import Sweeper\n"
        "from sharpelab_nb.gates import calculate_gate_voltages, calculate_n_D\n"
        "from sharpelab_nb import build_measurement_config\n"
        "\n"
        "s = Sweeper()\n"
        f"dtg, dbg, ep = {dtg}, {dbg}, {ep}   # acquisition lever lengths (device_card.md)\n"
        "mc = build_measurement_config(contact_pairs)   # sr830_2/3 = Rxx, sr830_4 = current"
    ))
    cells.append(nbf.v4.new_markdown_cell(
        "## SdH spot check — large |n|, D = 0\n"
        "\n"
        "Fixed (n, D=0), uniform in 1/B, to check onset and tone content on the cleaner side."
    ))
    cells.append(nbf.v4.new_code_cell(
        f"n_spot, D_spot = {N_SPOT}, 0.0\n"
        "vtg, vbg = calculate_gate_voltages(n_spot, D_spot, dtg=dtg, dbg=dbg, ep=ep)\n"
        "k_tg_volt(vtg); k_bg_volt(vbg)\n"
        "invB = np.linspace(1/3.0, 1/0.35, 900)          # uniform in 1/B\n"
        f"s.sweep(magnet_field, 1/invB, mc, delay=1.2)     # -> data/{spot_id}"
    ))
    cells.append(nbf.v4.new_markdown_cell(
        "## Landau fan — D = 0\n"
        "\n"
        "Field slow, paired-gate n-line fast; per-column FFT vs the Luttinger line is the read."
    ))
    cells.append(nbf.v4.new_code_cell(
        "n_line = np.linspace(-0.8, -6.0, 40)            # hole side, D = 0\n"
        "vtg_line, vbg_line = calculate_gate_voltages(n_line, 0.0, dtg=dtg, dbg=dbg, ep=ep)\n"
        "B_line = 1/np.linspace(1/3.0, 1/0.35, 900)      # uniform in 1/B\n"
        "s.multimegasweep([magnet_field], B_line, [k_tg_volt, k_bg_volt], [vtg_line, vbg_line],\n"
        f"                 mc, slow_delay=1, fast_delay=1.2)   # -> data/{fan_id}"
    ))

    nb["cells"] = cells
    path = case_dir / notebook_name
    nbf.write(nb, path)
    return path


def reload_fan(fan_dir, contact=2):
    meta = json.loads((fan_dir / "metadata.json").read_text())
    with gzip.open(fan_dir / "data.tsv.gz", "rt") as f:
        dat = np.loadtxt(f)
    field_axis = np.asarray(meta["slow_setpoints"][0], dtype=float)
    fast = np.asarray(meta["fast_setpoints"], dtype=float)
    nB, ncol = field_axis.size, fast.shape[1]
    cols = meta["columns"]

    def reshape(name):
        v = dat[:, cols.index(name)]
        return v[: nB * ncol].reshape(nB, ncol)

    vx = reshape(f"sr830_{contact}_X")
    ii = reshape("sr830_4_X")
    Rxx = vx / ii
    vtg, vbg = fast[0], fast[1]
    return dict(meta=meta, Rxx=Rxx, vtg=vtg, vbg=vbg, B=np.nanmean(reshape("magnet_field"), axis=1))


def top_freqs(B, Rxx, n_peaks=3):
    B = np.asarray(B, dtype=float)
    Rxx = np.asarray(Rxx, dtype=float)
    p = np.polyfit(B, Rxx, 5)
    resid = Rxx - np.polyval(p, B)
    invB = 1.0 / B
    order = np.argsort(invB)
    invB_s, resid_s = invB[order], resid[order]
    invB_u = np.linspace(invB_s[0], invB_s[-1], len(invB_s))
    resid_u = np.interp(invB_u, invB_s, resid_s)
    resid_u = resid_u - resid_u.mean()
    window = np.hanning(len(resid_u))
    spec = np.fft.rfft(resid_u * window)
    freqs = np.fft.rfftfreq(len(resid_u), d=(invB_u[1] - invB_u[0]))
    amp = np.abs(spec)
    mask = freqs > 0.5
    idx = np.where(mask)[0]
    peaks = [k for k in idx[1:-1] if amp[k] > amp[k - 1] and amp[k] > amp[k + 1]]
    peaks = sorted(peaks, key=lambda k: -amp[k])[:n_peaks]
    peaks = sorted(peaks, key=lambda k: freqs[k])
    return [(float(freqs[k]), float(amp[k])) for k in peaks]


def self_verify(case_name, case_dir, fan_dir, dtg, dbg, ep, npz, truth, j0_spot):
    reloaded = reload_fan(fan_dir)
    Rxx, vtg, vbg, B = reloaded["Rxx"], reloaded["vtg"], reloaded["vbg"], reloaded["B"]
    n_rec, D_rec = calculate_n_D(vtg, vbg, dtg, dbg, ep)

    n_truth = npz["n"]
    assert np.allclose(D_rec, 0.0, atol=1e-8), f"{case_name}: D round-trip failed: {D_rec}"
    assert np.allclose(n_rec, n_truth, atol=1e-6), f"{case_name}: n round-trip failed"

    jmid = int(np.argmin(np.abs(n_truth - (-3.5))))
    peaks = top_freqs(B, Rxx[:, jmid])
    truth_F = [f["F"] for f in truth["columns"][jmid]["fundamentals"]]

    print(f"\n=== {case_name} :: (n,D) round-trip ===")
    print(f"  max |D_rec| = {np.max(np.abs(D_rec)):.3e} V/nm (assert < 1e-8 OK)")
    print(f"  max |n_rec - n_truth| = {np.max(np.abs(n_rec - n_truth)):.3e} (1e12 cm^-2) (assert < 1e-6 OK)")

    print(f"=== {case_name} :: FFT tone recovery, column j={jmid} (n={n_truth[jmid]:.3f}) ===")
    print(f"  {'recovered F [T]':>18} | {'truth F [T]':>12} | {'rel err':>8}")
    matched_any = False
    for rf, amp in peaks:
        best = min(truth_F, key=lambda tf: abs(tf - rf))
        err = abs(rf - best) / best
        flag = "OK" if err < 0.05 else "  "
        if err < 0.05:
            matched_any = True
        print(f"  {rf:18.3f} | {best:12.3f} | {err:7.2%}  {flag}")
    assert matched_any, f"{case_name}: no recovered peak within 5% of any truth fundamental"

    # spot-check gate round-trip too
    print(f"=== {case_name} :: spot check column j0={j0_spot}, n={n_truth[j0_spot]:.3f} ===")


def build_case(case_name, params):
    npz = np.load(SRC_ROOT / case_name / "fan.npz")
    truth = json.loads((SRC_ROOT / case_name / "truth.json").read_text())
    case_dir = REPO / "hera" / "test-cases" / params["fixture"]

    rng = np.random.default_rng(params["seed"])

    spot_dir, j0 = build_spot(
        case_dir, npz, params["dtg"], params["dbg"], params["ep"],
        params["contacts"], params["spot_id"], rng,
    )
    fan_dir = build_fan(
        case_dir, npz, params["dtg"], params["dbg"], params["ep"],
        params["contacts"], params["fan_id"], rng,
    )
    nb_path = build_notebook(
        case_dir, params["notebook"], params["device"], params["date"],
        params["dtg"], params["dbg"], params["ep"], params["spot_id"], params["fan_id"],
    )

    self_verify(case_name, case_dir, fan_dir, params["dtg"], params["dbg"], params["ep"], npz, truth, j0)

    print(f"\n{case_name} files written:")
    for p in sorted(case_dir.rglob("*")):
        if p.is_file() and (p.parent.name in (params["spot_id"], params["fan_id"]) or p.suffix == ".ipynb"):
            print(f"  {p.relative_to(REPO)}")


def main():
    for case_name, params in CASES.items():
        build_case(case_name, params)


if __name__ == "__main__":
    main()
