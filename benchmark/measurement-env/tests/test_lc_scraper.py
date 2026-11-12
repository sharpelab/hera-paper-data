"""LC scraper (toploader): which log columns become metrics, with what unit.

Pins the PT family's publish set — PT1 only, including the compressor ON
flag — and the FP family's skip set, against real header shapes from the
rig's logs.
"""

from __future__ import annotations

from workers import lc_scraper


def _pt_line(on=1.0, status=1):
    values = ["2026-09-02 04:33:47"]
    for pt in range(1, 5):
        block = [on, 16.1, 38.2, 71.8, 36.2, 92.2, 298.6, 30.0] if pt == 1 else [0.0] * 8
        values += [f"{v:.6f}" for v in block]
    values += [str(status), "0", "0", "0"]
    return "\t".join(values) + "\n"


def test_pt_family_publishes_pt1_including_the_on_flag():
    family = lc_scraper.FAMILIES["PT"]
    _ts, metrics = lc_scraper._parse_line(_pt_line(), family)

    assert set(metrics) == {
        "PT1.ON", "PT1.W_in", "PT1.W_out", "PT1.He", "PT1.Oil",
        "PT1.P_low", "PT1.P_high", "PT1.I_mtr", "PT1.Status",
    }
    assert metrics["PT1.ON"] == (1.0, "status")
    assert metrics["PT1.Status"] == (1.0, "status")
    assert metrics["PT1.W_in"] == (16.1, "celsius")
    assert metrics["PT1.I_mtr"] == (30.0, "amps")


def test_fp_family_skips_state_and_status_columns():
    family = lc_scraper.FAMILIES["FP"]
    line = "\t".join(["2026-09-02 04:33:47"] + [f"{i}.0" for i in range(1, 16)]
                     + ["0", "0", "0", "1", "1"]) + "\n"
    _ts, metrics = lc_scraper._parse_line(line, family)

    assert set(metrics) == {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "Flow", "Pc",
                            "MG0", "MG1", "MG2", "MG3", "MG4", "MG5"}
    assert all(unit == "mbar" for _v, unit in metrics.values())
