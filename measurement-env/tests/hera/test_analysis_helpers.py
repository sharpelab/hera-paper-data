"""Tests for the hera.analysis fan helpers — fan_grids, resistance_grids,
sdh_fft, sdh_onset — plus the relocated channel/gain model.

Grid/resistance use the committed b1c2 2D fixture 117 (real gains in mc).
sdh_fft is checked against a synthetic cosine-in-1/B with a known frequency,
and against the committed QC0426 electron SdH fixture (B-space detrend resolves
the three tones with the near-F_L tone dominant). sdh_onset is checked on the
same fixture (onset ≈ 0.7 T, rejecting the spurious low-B spike).
"""

import json
from pathlib import Path

import numpy as np
import pytest

from hera.analysis import (
    Channel,
    GateCalibration,
    SdhOnsetError,
    current_channel,
    fan_grids,
    field_invB,
    luttinger_frequency,
    open_run,
    resistance_grids,
    resolve_channels,
    sdh_fft,
    sdh_onset,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
B1C2_DATA = REPO_ROOT / "hera/docs/notes/2026-05-05-b1c2-session/data"
RUN_117 = B1C2_DATA / "117"  # 2D, 401 × 51, sr830_1 current + sr830_2..4 voltage

# QC0426 electron SdH spot-check (n = +5e12, F_L = 51.7 T, B 0→4 T at 8 mT),
# vendored from the 2026-06-19 session-3 review. Three real tones: ML ~8 T,
# BL ~48 T, ABC ~56 T (mixed ABA/ABC stacking).
QC0426_SDH = REPO_ROOT / "tests/hera/fixtures/qc0426-sdh-electron"
QC0426_F_L = 51.7  # Tesla, full-density Onsander freq at n = +5e12 cm^-2


# --------------------------------------------------------------------------
# channel / gain model
# --------------------------------------------------------------------------


def test_resolve_channels_b1c2():
    meta = json.loads((RUN_117 / "metadata.json").read_text())
    chans = resolve_channels(meta)
    by_cid = {c.cid: c for c in chans}
    assert set(by_cid) == {"sr830_1", "sr830_2", "sr830_3", "sr830_4"}
    assert by_cid["sr830_1"].gain == -1e6 and by_cid["sr830_1"].is_current
    assert by_cid["sr830_2"].gain == 100.0 and not by_cid["sr830_2"].is_current


def test_resolve_channels_include_filter():
    meta = json.loads((RUN_117 / "metadata.json").read_text())
    chans = resolve_channels(meta, include=["sr830_2"])
    assert [c.cid for c in chans] == ["sr830_2"]


def test_current_channel_unique():
    meta = json.loads((RUN_117 / "metadata.json").read_text())
    cur = current_channel(resolve_channels(meta))
    assert cur is not None and cur.cid == "sr830_1"


def test_current_channel_none_when_ambiguous():
    a = Channel("a_X", 0, "a", 0, -1e6, "cur a", True)
    b = Channel("b_X", 1, "b", 1, -1e6, "cur b", True)
    assert current_channel([a, b]) is None
    assert current_channel([]) is None


# --------------------------------------------------------------------------
# fan_grids
# --------------------------------------------------------------------------


def test_fan_grids_117():
    fg = fan_grids(RUN_117)
    assert fg.nfast == 51
    assert fg.nrows == 401
    assert fg.grid("magnet_field").shape == (401, 51)
    # slow axis is the magnet_field; one value per row.
    assert fg.slow.shape == (401,)
    assert fg.slow_param == "magnet_field"


def test_fan_grids_accepts_run_object():
    run = open_run(RUN_117)
    fg = fan_grids(run)
    assert fg.nrows == 401 and fg.nfast == 51


def test_fan_grids_metadata_aliases_meta():
    fg = fan_grids(RUN_117)
    assert fg.metadata is fg.meta


def test_fan_grids_truncates_partial(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    meta = {
        "columns": ["mag", "n", "sr1_X"],
        "type": "2D",
        "slow_params": ["mag"],
        "fast_params": ["n"],
        "slow_setpoints": [[0.0, 1.0, 2.0]],
        "fast_setpoints": [[-1.0, 0.0, 1.0]],  # nfast = 3
        "measurement_config": {},
    }
    (d / "metadata.json").write_text(json.dumps(meta))
    # 2 full rows + 2 of a 3rd (7 rows) -> nrows must floor to 2.
    rows = [f"{s}\t{n}\t1e-6" for s in (0, 1) for n in (-1, 0, 1)]
    rows += [f"2\t{n}\t1e-6" for n in (-1, 0)]
    (d / "data.tsv").write_text("\n".join(rows) + "\n")
    fg = fan_grids(d)
    assert fg.nrows == 2
    assert fg.grid("mag").shape == (2, 3)


def test_fan_grids_column_filter():
    fg = fan_grids(RUN_117, columns=["magnet_field", "sr830_2_X"])
    assert fg.cols == ["magnet_field", "sr830_2_X"]
    assert fg.grid("sr830_2_X").shape == (401, 51)


# --------------------------------------------------------------------------
# resistance_grids
# --------------------------------------------------------------------------


def test_resistance_grids_117():
    fg = fan_grids(RUN_117)
    rg = resistance_grids(fg)
    assert rg.current_channel == "sr830_1"
    assert set(rg.R) == {"sr830_2", "sr830_3", "sr830_4"}
    assert rg.current.shape == (401, 51)
    # R = (V/gain_V) / I, with I = sr830_1_X / (-1e6), gain_V = 100.
    I = fg.grid("sr830_1_X") / -1e6
    expected = (fg.grid("sr830_2_X") / 100.0) / I
    assert np.allclose(rg.R["sr830_2"], expected, equal_nan=True)


def test_resistance_grids_signed(tmp_path):
    # R = V/I is returned signed (no abs) so Rxy/Hall keep their sign.
    # current sr0_X=+5e-7 / gain -1e6 -> I < 0; voltage sr1_X=+1e-6 -> R < 0.
    d = tmp_path / "run"
    d.mkdir()
    meta = {
        "columns": ["mag", "n", "sr0_X", "sr1_X"],
        "type": "2D",
        "slow_params": ["mag"],
        "fast_params": ["n"],
        "slow_setpoints": [[0.0, 1.0]],
        "fast_setpoints": [[-1.0, 0.0]],
        "measurement_config": {"sr0": "drain current", "sr0_gain": -1e6, "sr1": "a-b"},
    }
    (d / "metadata.json").write_text(json.dumps(meta))
    rows = [f"{s}\t{n}\t5e-7\t1e-6" for s in (0, 1) for n in (-1, 0)]
    (d / "data.tsv").write_text("\n".join(rows) + "\n")
    rg = resistance_grids(fan_grids(d))
    assert np.all(rg.R["sr1"] < 0)


def test_resistance_grids_channel_filter():
    fg = fan_grids(RUN_117)
    rg = resistance_grids(fg, channels=["sr830_2"])
    assert set(rg.R) == {"sr830_2"}
    assert rg.current_channel == "sr830_1"  # current still resolved


def test_resistance_grids_needs_current_channel(tmp_path):
    d = tmp_path / "run"
    d.mkdir()
    meta = {
        "columns": ["mag", "n", "sr1_X"],
        "type": "2D",
        "slow_params": ["mag"],
        "fast_params": ["n"],
        "slow_setpoints": [[0.0, 1.0]],
        "fast_setpoints": [[-1.0, 0.0]],
        "measurement_config": {"sr1": "a-b"},  # gain 1 -> voltage, no current
    }
    (d / "metadata.json").write_text(json.dumps(meta))
    rows = [f"{s}\t{n}\t1e-6" for s in (0, 1) for n in (-1, 0)]
    (d / "data.tsv").write_text("\n".join(rows) + "\n")
    with pytest.raises(ValueError, match="one current channel"):
        resistance_grids(fan_grids(d))


# --------------------------------------------------------------------------
# field_invB
# --------------------------------------------------------------------------


def test_field_invB_uniform_in_inverse_B():
    B = field_invB(1.5, 4.0, 50)
    assert B.shape == (50,)
    d = np.diff(1.0 / B)
    assert np.allclose(d, d[0])  # evenly spaced in 1/B


def test_field_invB_hits_endpoints():
    B = field_invB(1.5, 4.0, 50)
    assert B[0] == pytest.approx(1.5)
    assert B[-1] == pytest.approx(4.0)


def test_field_invB_direction_from_endpoint_order():
    asc = field_invB(1.5, 4.0, 20)
    desc = field_invB(4.0, 1.5, 20)
    assert asc[0] < asc[-1]
    assert desc[0] > desc[-1]
    assert np.allclose(asc, desc[::-1])


def test_field_invB_feeds_sdh_fft_uniform_path():
    # field_invB output is the measurement-side companion to sdh_fft's uniform
    # path: sdh_fft must FFT it directly (no resample), so all native samples
    # survive — the interp path would truncate to nfft.
    B = field_invB(1.5, 4.0, 600)
    R_grid = np.cos(2 * np.pi * 30.0 / B)[:, None]
    freqs, _ = sdh_fft(R_grid, B, nfft=256, bg_degree=None, window="hann", log=False)
    assert freqs.size == 600 // 2 + 1


def test_field_invB_rejects_nonpositive_endpoint():
    with pytest.raises(ValueError, match="must be > 0"):
        field_invB(0.0, 4.0, 50)
    with pytest.raises(ValueError, match="must be > 0"):
        field_invB(1.5, -4.0, 50)


# --------------------------------------------------------------------------
# sdh_fft
# --------------------------------------------------------------------------


def test_sdh_fft_recovers_known_frequency():
    # Two columns, each a cosine in 1/B at a distinct SdH frequency.
    B = np.linspace(2.0, 6.0, 240)
    f0, f1 = 21.0, 45.0
    col0 = np.cos(2 * np.pi * f0 / B)
    col1 = np.cos(2 * np.pi * f1 / B)
    R_grid = np.stack([col0, col1], axis=1)  # (nB, 2)
    freqs, spec = sdh_fft(R_grid, B, nfft=1024, bg_degree=None, window="hann", log=False)
    assert freqs[0] == 0.0  # rfft DC bin, in Tesla
    assert spec.shape == (2, freqs.size)
    df = freqs[1] - freqs[0]
    assert abs(freqs[np.argmax(spec[0])] - f0) <= df
    assert abs(freqs[np.argmax(spec[1])] - f1) <= df


def test_sdh_fft_b_range_select():
    B = np.linspace(0.0, 8.0, 400)
    R_grid = np.cos(2 * np.pi * 30.0 / np.maximum(B, 0.1))[:, None]
    freqs, spec = sdh_fft(R_grid, B, b_range=(2.0, 6.0), nfft=512, bg_degree=None,
                          window="hann", log=False)
    df = freqs[1] - freqs[0]
    assert abs(freqs[np.argmax(spec[0])] - 30.0) <= 2 * df


def test_sdh_fft_too_few_rows_raises():
    B = np.array([3.0, 4.0])
    with pytest.raises(ValueError, match=">=4 field rows"):
        sdh_fft(np.ones((2, 1)), B)


def test_sdh_fft_shape_mismatch_raises():
    with pytest.raises(ValueError, match="!= len"):
        sdh_fft(np.ones((5, 3)), np.arange(4.0))


def test_sdh_fft_uniform_invB_no_interp():
    # A run swept uniformly in 1/B is FFT'd directly (no resample). With more
    # native samples than nfft, the output keeps all of them — proving the
    # interpolation path (which would truncate to nfft) was not taken.
    invB = np.linspace(1.0 / 4.0, 1.0 / 1.5, 600)
    B = 1.0 / invB
    f0 = 30.0
    R_grid = np.cos(2 * np.pi * f0 * invB)[:, None]
    freqs, spec = sdh_fft(R_grid, B, nfft=256, bg_degree=None, window="hann", log=False)
    assert freqs.size == 600 // 2 + 1  # rfft of 600 native points, not nfft=256
    df = freqs[1] - freqs[0]
    assert abs(freqs[np.argmax(spec[0])] - f0) <= 2 * df


def test_sdh_fft_uniform_and_nonuniform_agree():
    # The same cosine-in-1/B recovers the same peak frequency whether the field
    # is sampled uniformly in 1/B (new field_invB runs — resample skipped) or
    # uniformly in B (legacy runs — resampled onto a uniform 1/B grid). The two
    # acquisition layouts must agree on the physics.
    f0 = 30.0
    B_lo, B_hi, N = 1.5, 4.0, 600

    B_invB = 1.0 / np.linspace(1.0 / B_lo, 1.0 / B_hi, N)  # uniform in 1/B
    B_lin = np.linspace(B_lo, B_hi, N)                     # uniform in B
    R_invB = np.cos(2 * np.pi * f0 / B_invB)[:, None]
    R_lin = np.cos(2 * np.pi * f0 / B_lin)[:, None]

    fr_u, sp_u = sdh_fft(R_invB, B_invB, nfft=1024, bg_degree=None, window="hann", log=False)
    fr_n, sp_n = sdh_fft(R_lin, B_lin, nfft=1024, bg_degree=None, window="hann", log=False)

    peak_u = fr_u[np.argmax(sp_u[0])]
    peak_n = fr_n[np.argmax(sp_n[0])]
    assert abs(peak_u - f0) <= 2 * (fr_u[1] - fr_u[0])
    assert abs(peak_n - f0) <= 2 * (fr_n[1] - fr_n[0])
    assert abs(peak_u - peak_n) <= 2 * (fr_n[1] - fr_n[0])


# --------------------------------------------------------------------------
# sdh_fft / sdh_onset on the QC0426 electron SdH fixture
# --------------------------------------------------------------------------


def _qc0426_rxx(cid: str) -> tuple[np.ndarray, np.ndarray]:
    """(B, |Rxx|) for voltage channel `cid` from the QC0426 electron fixture.

    Uses the real gain model: I = sr0_X / sr0_gain (transimpedance), Rxx =
    |(V/gain_V) / I|. The field column `magnet_mag` is duplicated in this run
    (planned + readback); the first occurrence is the planned setpoint.
    """
    run = open_run(QC0426_SDH)
    chans = resolve_channels(run.meta)
    cur = current_channel(chans)
    assert cur is not None
    I = run.col(cur.col) / cur.gain
    v = next(c for c in chans if c.cid == cid)
    B = run.data[:, run.col_indices("magnet_mag")[0]]
    return B, np.abs((run.col(v.col) / v.gain) / I)


def _peak(freqs: np.ndarray, spec: np.ndarray, center: float, half: float = 4.0) -> float:
    band = (freqs > center - half) & (freqs < center + half)
    return float(spec[band].max()) if band.any() else 0.0


def test_sdh_fft_bspace_resolves_qc0426_tones():
    # The fix: B-space background subtraction resolves all three SdH tones
    # (ML ~8 T, BL ~48 T, ABC ~56 T) with the near-F_L tone DOMINANT over the
    # spurious 8 T — the 1/B-space detrend left low-freq background residual
    # that inflated the 8 T tone and made it dominate (driving a wrong call).
    B, Rxx = _qc0426_rxx("sr1")
    freqs, spec = sdh_fft(Rxx[:, None], B, b_range=(1.5, 4.0), bg_degree=5, log=True)
    P = spec[0] / spec[0].max()
    floor = float(np.median(P[(freqs > 60) & (freqs < 90)]))
    p_ml = _peak(freqs, P, 8.0)
    p_bl = _peak(freqs, P, QC0426_F_L - 4.0)  # BL pocket ~48 T
    p_abc = _peak(freqs, P, 56.0)             # ABC tone near F_L
    # All three tones rise clearly above the noise floor.
    assert p_ml > 5 * floor
    assert p_bl > 5 * floor
    assert p_abc > 5 * floor
    # The whole point: a near-F_L tone dominates the 8 T tone.
    assert max(p_bl, p_abc) > p_ml


def test_sdh_fft_1bspace_detrend_would_inflate_8T():
    # Regression-direction guard: the OLD 1/B-space polynomial detrend (now
    # removed) leaves the 8 T tone dominant on the same window — confirming the
    # detrend space, and nothing else, is what flips the call.
    B, Rxx = _qc0426_rxx("sr1")
    m = (B >= 1.5) & (B <= 4.0)
    invB = 1.0 / B[m]
    order = np.argsort(invB)
    ib = invB[order]
    u = np.linspace(ib[0], ib[-1], 512)
    du = u[1] - u[0]
    y = np.log10(np.maximum(Rxx[m], 1.0))
    yi = np.interp(u, ib, y[order])
    yi = yi - np.polyval(np.polyfit(u, yi, 5), u)  # the old 1/B-space detrend
    freqs = np.fft.rfftfreq(512, du)
    P = np.abs(np.fft.rfft(yi * np.hanning(512)))
    P = P / P.max()
    assert _peak(freqs, P, 8.0) >= max(_peak(freqs, P, 48.0), _peak(freqs, P, 56.0))


def test_sdh_onset_qc0426_matches_expert():
    # Aaron's eyeball on this fixture is ≈ 0.7 T; the matched-filter onset is
    # statistical (5σ), so it may sit near but not exactly on the eye read.
    B, Rxx = _qc0426_rxx("sr1")
    res = sdh_onset(Rxx, B)
    assert 0.6 <= res.onset_b <= 1.1
    assert res.clip_high_b == pytest.approx(B.max(), abs=0.05)
    # The tone set includes the ML ~8 T and a heavy tone near BL/F_L.
    freqs = [t.freq for t in res.tones]
    assert any(6.0 <= f <= 10.5 for f in freqs)
    assert any(42.0 <= f <= 60.0 for f in freqs)
    # Dominant-tone compat surface.
    assert res.snr.shape == res.b_centers.shape
    assert res.consensus_freq == res.tones[0].freq


def test_sdh_onset_rejects_low_b_spike():
    # This fixture has a spurious low-B spike below ~0.62 T. The gap-walk must
    # not drag any tone's onset into it: an isolated feature disconnected from
    # the tone's high-B track is rejected (gap_widths), so the headline onset
    # stays above the spike.
    B, Rxx = _qc0426_rxx("sr1")
    res = sdh_onset(Rxx, B)
    assert res.onset_b > 0.62
    carrier = next(t for t in res.tones if t.freq == res.onset_freq)
    assert not carrier.censored  # a real die-off was located, not the edge


def test_sdh_onset_summary_smoke():
    B, Rxx = _qc0426_rxx("sr1")
    res = sdh_onset(Rxx, B)
    s = res.summary()
    assert "onset_b" in s and f"{res.onset_b:.2f}" in s
    assert s.count("tone ") >= len(res.tones)


# --------------------------------------------------------------------------
# sdh_onset on synthetic records (known tones, known onsets)
# --------------------------------------------------------------------------


def _synth(tones, *, b_lo=0.5, b_hi=8.0, n=1400, sigma=1.0, seed=7):
    """Uniform-1/B record: smooth MR background + Dingle-damped tones + noise.

    `tones` is a list of `(freq_T, a0_Ohm, lam)`: each tone contributes
    `a0·exp(-lam·(1/B))·cos(2π·freq/B)` — the physical Dingle form, spectrally
    clean (a step/sigmoid taper would splash sidebands). The designed 5σ onset
    is at `1/B = ln(a0/(5·σ_A))/lam` with `σ_A` the matched-filter noise floor;
    the tests assert bands around that crossing.
    """
    rng = np.random.default_rng(seed)
    u = np.linspace(1.0 / b_hi, 1.0 / b_lo, n)
    B = 1.0 / u
    R = 120.0 + 3.0 * B + 1.5 * B ** 2  # smooth MR background
    for f, a0, lam in tones:
        R = R + a0 * np.exp(-lam * u) * np.cos(2 * np.pi * f * u + 0.7)
    return B, R + rng.normal(0.0, sigma, n)


def test_sdh_onset_single_tone_known_onset():
    # 30 T tone, a0=380, lam=12: 5σ crossing designed at ~2.0 T.
    B, R = _synth([(30.0, 380.0, 12.0)])
    res = sdh_onset(R, B)
    assert res.onset_freq == pytest.approx(30.0, abs=1.5)
    assert 1.6 <= res.onset_b <= 2.6
    carrier = next(t for t in res.tones if t.freq == res.onset_freq)
    assert not carrier.censored


def test_sdh_onset_light_tone_outlives_heavy():
    # The capstone-r6 failure class: the dominant heavy tone dies ~3 T while a
    # weaker light tone survives to ~1.2 T. The headline must follow the light
    # tone (per-dominant-tone semantics silently mis-served light-tone hunts).
    B, R = _synth([(33.0, 150.0, 15.0), (8.0, 14.0, 4.0)])
    res = sdh_onset(R, B)
    light = min(res.tones, key=lambda t: abs(t.freq - 8.0))
    heavy = min(res.tones, key=lambda t: abs(t.freq - 33.0))
    assert light.freq == pytest.approx(8.0, abs=1.0)
    assert heavy.freq == pytest.approx(33.0, abs=1.5)
    assert light.onset_b <= 1.8
    assert 2.2 <= heavy.onset_b <= 4.0
    assert res.onset_b == light.onset_b
    assert res.onset_b < heavy.onset_b


def test_sdh_onset_two_heavy_tones_abab_shape():
    # Bernal-tetralayer shape: two comparable heavy tones, no light tone —
    # the shape the old argmax-median consensus was worst at.
    B, R = _synth([(24.0, 200.0, 12.0), (40.0, 80.0, 12.0)])
    res = sdh_onset(R, B)
    assert any(abs(t.freq - 24.0) < 1.5 for t in res.tones)
    assert any(abs(t.freq - 40.0) < 2.0 for t in res.tones)
    assert 1.6 <= res.onset_b <= 3.0


def test_sdh_onset_narrow_band_finite():
    # The 0714-r5 failure class: oscillatory band narrower than the old fixed
    # 0.18/T window (a 55 T tone dead below ~3.5 T on a record reaching
    # 0.5 T) must give a finite onset, not nan.
    B, R = _synth([(55.0, 400.0, 20.0)])
    res = sdh_onset(R, B)
    assert np.isfinite(res.onset_b)
    assert 2.7 <= res.onset_b <= 4.5
    assert any(abs(t.freq - 55.0) < 2.0 for t in res.tones)


def test_sdh_onset_noise_only_raises():
    B, R = _synth([], sigma=2.0)
    with pytest.raises(SdhOnsetError, match="no SdH tones"):
        sdh_onset(R, B)


def test_sdh_onset_censored_reports_record_edge():
    # Tone alive through the whole record: onset is the record's low edge,
    # flagged censored, with a warning — never a fabricated die-off.
    B, R = _synth([(30.0, 30.0, 1.0)])  # barely damped: alive everywhere
    with pytest.warns(UserWarning, match="persist"):
        res = sdh_onset(R, B)
    carrier = next(t for t in res.tones if t.freq == res.onset_freq)
    assert carrier.censored
    assert res.onset_b == pytest.approx(B.min(), abs=0.02)


def test_sdh_onset_soft_clip_truncates_and_warns():
    B, R = _synth([(30.0, 380.0, 12.0)])
    # Rail the record at 250 Ohm (the MR background tops ~265 near 8 T), then
    # declare 250 as full scale: high-B samples sit at >= 95% of it.
    R = np.minimum(R, 250.0)
    with pytest.warns(UserWarning, match="soft clip"):
        res = sdh_onset(R, B, r_full_scale=250.0)
    assert res.clip_high_b < B.max() - 0.5
    # Untruncated call keeps the full window (no clip detection without scale).
    res2 = sdh_onset(R, B)
    assert res2.clip_high_b == pytest.approx(B.max(), abs=0.05)


def test_sdh_onset_harmonic_annotated():
    # A strong tone plus its half-amplitude 2f: the harmonic is annotated so
    # a comb cannot masquerade as an independent pocket. The relationship is
    # bidirectional — the fundamental lists the harmonic in reverse.
    B, R = _synth([(20.0, 60.0, 4.0), (40.0, 30.0, 4.0)])
    res = sdh_onset(R, B)
    h = min(res.tones, key=lambda t: abs(t.freq - 40.0))
    fund = min(res.tones, key=lambda t: abs(t.freq - 20.0))
    assert h.harmonic_of == pytest.approx(20.0, abs=1.5)
    assert any(abs(fh - 40.0) < 2.0 for fh in fund.harmonics)


@pytest.mark.parametrize("k,f_harm", [(2, 40.0), (3, 60.0)])
def test_sdh_onset_reverse_harmonic_dominant(k, f_harm):
    # The "sr1 gap": a DOMINANT k*f harmonic over a WEAK 20 T fundamental. The
    # weak fundamental (never stronger than its own harmonic, so amplitude
    # ordering hides it) must still carry the reverse annotation, and the
    # dominant harmonic must point back at it.
    B, R = _synth([(20.0, 22.0, 4.0), (f_harm, 130.0, 4.0)])
    res = sdh_onset(R, B)
    fund = min(res.tones, key=lambda t: abs(t.freq - 20.0))
    harm = min(res.tones, key=lambda t: abs(t.freq - f_harm))
    assert fund.freq == pytest.approx(20.0, abs=1.5)
    assert harm.freq == pytest.approx(f_harm, abs=2.0)
    assert harm.contrast > fund.contrast  # the harmonic is the dominant tone
    assert harm.harmonic_of == pytest.approx(20.0, abs=1.5)
    assert round(harm.freq / fund.freq) == k
    assert any(abs(fh - f_harm) < 2.0 for fh in fund.harmonics)


def test_sdh_onset_shape_mismatch_raises():
    with pytest.raises(ValueError, match="!= B shape"):
        sdh_onset(np.ones(5), np.ones(4))


def test_sdh_onset_too_few_rows_raises():
    with pytest.raises(SdhOnsetError, match="field rows"):
        sdh_onset(np.ones(4), np.linspace(1.0, 2.0, 4))


# --------------------------------------------------------------------------
# GateCalibration / luttinger_frequency
# --------------------------------------------------------------------------

# scipy.constants values used to hand-compute the expected SI results.
_E = 1.602176634e-19
_H = 6.62607015e-34
_EPS0 = 8.8541878188e-12


def test_density_matches_hand_computed():
    # QC0426 session calibration: c_tg=1.7027e-3, c_bg=2.2105e-3 F/m^2,
    # n_offset=-7.095e14 m^-2.
    cal = GateCalibration(c_tg=1.7027e-3, c_bg=2.2105e-3, n_offset=-7.095e14)
    n = cal.density(0.5, -1.0)
    expected = (1.7027e-3 * 0.5 + 2.2105e-3 * -1.0) / _E + -7.095e14
    assert np.isclose(float(n), expected)


def test_displacement_field_matches_hand_computed():
    cal = GateCalibration(c_tg=1.7027e-3, c_bg=2.2105e-3, D_offset=0.0)
    D = cal.displacement_field(0.5, -1.0)
    expected = (1.7027e-3 * 0.5 - 2.2105e-3 * -1.0) / (2.0 * _EPS0)
    assert np.isclose(float(D), expected)


def test_offsets_default_zero():
    cal = GateCalibration(c_tg=1e-3, c_bg=1e-3)
    assert cal.n_offset == 0.0 and cal.D_offset == 0.0
    # At V=0 with no offsets, both n and D are zero.
    n, D = cal.n_D(0.0, 0.0)
    assert float(n) == 0.0 and float(D) == 0.0


def test_n_D_pair_matches_components():
    cal = GateCalibration(c_tg=1.7e-3, c_bg=2.2e-3, n_offset=-7e14, D_offset=0.01)
    n, D = cal.n_D(0.3, -0.7)
    assert np.allclose(n, cal.density(0.3, -0.7))
    assert np.allclose(D, cal.displacement_field(0.3, -0.7))


def test_calibration_broadcasts_over_arrays():
    cal = GateCalibration(c_tg=1.7e-3, c_bg=2.2e-3)
    V_tg = np.array([0.0, 0.5, 1.0])
    V_bg = np.array([-1.0, 0.0, 1.0])
    n, D = cal.n_D(V_tg, V_bg)
    assert n.shape == (3,) and D.shape == (3,)
    assert np.isclose(n[1], 1.7e-3 * 0.5 / _E)


def test_calibration_is_frozen():
    cal = GateCalibration(c_tg=1e-3, c_bg=1e-3)
    with pytest.raises(Exception):
        cal.c_tg = 2e-3  # frozen dataclass: set-once per session


def test_from_thicknesses_matches_calc_ctg_cbg():
    # Reproduces the ana/measure notebooks' calc_ctg/calc_cbg formulas
    # (kappa_hBN=3, kappa_SiO2=3.9) for a metal back gate (t_bgSiO2=0).
    t_tg, t_bg = 15.6e-9, 12e-9
    cal = GateCalibration.from_thicknesses(t_tg, t_bg)
    assert np.isclose(cal.c_tg, _EPS0 * 3.0 / t_tg)
    assert np.isclose(cal.c_bg, _EPS0 / (t_bg / 3.0))
    assert cal.n_offset == 0.0 and cal.D_offset == 0.0


def test_from_thicknesses_sio2_term_and_offsets():
    # SiO2 back-gate term contributes; offsets pass through.
    t_tg, t_bg, t_ox = 15.6e-9, 12e-9, 285e-9
    cal = GateCalibration.from_thicknesses(
        t_tg, t_bg, t_ox, n_offset=-7e14, D_offset=0.01
    )
    assert np.isclose(cal.c_bg, _EPS0 / (t_bg / 3.0 + t_ox / 3.9))
    assert cal.n_offset == -7e14 and cal.D_offset == 0.01


def test_luttinger_recovers_session_anchor():
    # n = -4e16 m^-2 (the −4×10¹² cm^-2 go/no-go anchor) -> F = 41.4 T.
    F = luttinger_frequency(-4e16)
    assert np.isclose(float(F), 41.4, atol=0.1)
    # closed form
    assert np.isclose(float(F), 4e16 * _H / (4.0 * _E))


def test_luttinger_takes_abs():
    # Electron and hole side of the same |n| give the same positive frequency.
    assert np.allclose(luttinger_frequency(4e16), luttinger_frequency(-4e16))
    assert np.all(luttinger_frequency(np.array([-1e16, 1e16])) > 0)


def test_luttinger_chains_from_density():
    cal = GateCalibration(c_tg=1.7027e-3, c_bg=2.2105e-3, n_offset=-7.095e14)
    n = cal.density(np.array([0.5, 1.0]), np.array([-0.5, 0.0]))
    F = luttinger_frequency(n)
    assert F.shape == (2,)
    assert np.allclose(F, np.abs(n) * _H / (4.0 * _E))
