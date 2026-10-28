"""sdh_onset regression against archived QC0426 session records.

The three archives under hera/docs/notes are the records the extractor
historically failed on (nan on narrow bands and multi-tone flips, per-dominant-
tone onsets mis-serving light-tone hunts, an unflagged soft clip); the by-eye
onsets in each session's ana notebook are the truth anchors. Bands are wide
enough to absorb knob tuning but tight enough to catch a semantics regression.

Skipped wholesale if the archives are absent (they are in-repo, but keep the
suite runnable from a trimmed checkout).
"""

import warnings
from pathlib import Path

import numpy as np
import pytest

from hera.analysis import open_run, sdh_onset

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTES = REPO_ROOT / "hera/docs/notes"
I_BIAS = 20e-9

pytestmark = pytest.mark.skipif(
    not (NOTES / "2026-07-17-QC0426-capstone-2/data/6").is_dir(),
    reason="archived session records not present",
)


def _rxx(archive: str, run: int, cid: str) -> tuple[np.ndarray, np.ndarray]:
    r = open_run(NOTES / archive / "data" / str(run))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # duplicate magnet_field column
        B = r.col("magnet_field")
    order = np.argsort(B)
    R = r.col_at(r.col_indices(f"{cid}_X")[-1]) / I_BIAS
    return B[order], R[order]


def _onset(archive, run, cid, **kw):
    B, R = _rxx(archive, run, cid)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return sdh_onset(R, B, **kw)


# --- 2026-07-14 session 2: nan on narrow band (r5) and consensus flip (r6) ---


@pytest.mark.parametrize("cid,lo,hi", [("sr1", 0.9, 1.7), ("sr2", 1.4, 2.3)])
def test_0714_run5_finite_onset(cid, lo, hi):
    # Old: nan (oscillatory band narrower than the fixed window). The light
    # ~11 T tone carries the record edge; the heavy ~54 T tone (by-eye 3.5 T
    # in a B>3.5 detrended plot) is tracked separately.
    res = _onset("2026-07-14-QC0426-session-2", 5, cid)
    assert lo <= res.onset_b <= hi
    assert any(abs(t.freq - 11.2) < 1.5 for t in res.tones)


def test_0714_run6_sr2_matches_hand_tuned_reading():
    # Old: 1.33 T, but only with a hand-tuned win_invB=0.10; defaults gave nan
    # on sr1 (consensus flip). The session read 1.33 as the fan's B_lo.
    res = _onset("2026-07-14-QC0426-session-2", 6, "sr2")
    assert 1.2 <= res.onset_b <= 1.6
    res1 = _onset("2026-07-14-QC0426-session-2", 6, "sr1")
    assert np.isfinite(res1.onset_b)  # old code: nan


# --- 2026-07-16 session 3: the refire (clean 1303-pt record, nan) ---


def test_s3_run6_finite_no_eyeball_needed():
    # Old: nan on a clean 1303-pt record (consensus 11.1 T was sensible);
    # onset was read by eye at 1.8-2 T. The matched filter finds the ~11 T
    # tone statistically alive below the eye read (phase-coherent, 38σ at the
    # last window on sr1) — on this record, which ends at 1.0 T, that means a
    # censored track at the edge, or a die-off between edge and eye band.
    for cid in ("sr1", "sr2"):
        B, R = _rxx("2026-07-16-QC0426-session-3", 6, cid)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = sdh_onset(R, B)
        assert np.isfinite(res.onset_b)
        carrier = next(t for t in res.tones if t.freq == res.onset_freq)
        if carrier.censored:
            assert res.onset_b == pytest.approx(1.0, abs=0.05)
        else:
            assert 1.2 <= res.onset_b <= 2.3


def test_s3_run10_onset_ladder_preserved():
    # The session logged the device's onset ladder: onset rises at lower |n|
    # (2.06-3.3 T at 3e12 vs 1.4-1.9 at 6e12). sr2 must stay in that band.
    res = _onset("2026-07-16-QC0426-session-3", 10, "sr2")
    assert 1.9 <= res.onset_b <= 2.8


# --- 2026-07-17 capstone 2: per-dominant-tone semantics + soft clip ---


def test_capstone_run5_clean_to_edge_and_clip():
    # Old: 0.77 T "onset" was the record edge reached by a broken SNR floor —
    # right by luck. The record is genuinely clean to its low edge (0.70 T):
    # the light-tone family is censored there. sr1 additionally soft-clips
    # (2.73 kOhm on a 2.5 kOhm scale) — passing the full scale truncates the
    # window and warns; the old path sailed through unflagged.
    B, R = _rxx("2026-07-17-QC0426-capstone-2", 5, "sr1")
    with pytest.warns(UserWarning, match="soft clip"):
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            res = sdh_onset(R, B, r_full_scale=2500.0)
    assert res.clip_high_b < 7.0
    assert res.onset_b == pytest.approx(0.70, abs=0.05)
    res2 = _onset("2026-07-17-QC0426-capstone-2", 5, "sr2")
    assert res2.onset_b == pytest.approx(0.70, abs=0.05)


@pytest.mark.parametrize("cid", ["sr1", "sr2"])
def test_capstone_run6_light_tones_exposed(cid):
    # Old: onset_b = 3.3-3.9 T — the dominant 33 T tone's SNR edge — while
    # oscillations visibly run from ~1.5 T. The headline must sit at/below the
    # visible band, and the light-tone tracks (< 16 T) must be exposed with
    # their own onsets below the old heavy-edge answer.
    res = _onset("2026-07-17-QC0426-capstone-2", 6, cid)
    assert res.onset_b <= 2.0
    lights = [t for t in res.tones if t.freq < 16.0 and not t.near_residual]
    assert lights and min(t.onset_b for t in lights) < 2.5


def test_capstone_run6_sr1_dominant_harmonic_bidirectional():
    # The motivating "sr1 gap": the dominant 32.8 T tone sits at ~2x the weaker
    # 16.3 T tone. Amplitude ordering used to hide that (32.8 read as a bare
    # fundamental); now it points back at 16.3, and 16.3 lists 32.8 as its
    # harmonic — the relationship is discoverable from either end.
    res = _onset("2026-07-17-QC0426-capstone-2", 6, "sr1")
    dom = min(res.tones, key=lambda t: abs(t.freq - 32.8))
    fund = min(res.tones, key=lambda t: abs(t.freq - 16.3))
    assert abs(dom.freq - 32.8) < 1.5 and abs(fund.freq - 16.3) < 1.5
    assert dom.contrast > fund.contrast  # the harmonic is the dominant tone
    assert dom.harmonic_of == pytest.approx(fund.freq, abs=1.0)
    assert any(abs(fh - dom.freq) < 1.5 for fh in fund.harmonics)


def test_capstone_run6_no_silent_wiggle_grab():
    # sr2's 25.2 T tone dies at ~2.3 T; an isolated big wiggle near 1.3 T
    # lights one window. The gap-walk must not connect across the dead zone —
    # the wiggle is disclosed as revived, not eaten as the onset.
    res = _onset("2026-07-17-QC0426-capstone-2", 6, "sr2")
    t25 = min(res.tones, key=lambda t: abs(t.freq - 25.2))
    if abs(t25.freq - 25.2) < 1.5:  # tone present in this tuning
        assert t25.onset_b > 1.9
        assert t25.revived
