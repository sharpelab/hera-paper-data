"""QDevil QDAC-II as a gate source.

Re-exports the vendored QDAC-II driver (``drivers.QDAC2``) under a stable
import path and provides :func:`bring_up_qdac_gate`, the pit-of-success bring-up that
configures one channel as a gate — mirroring the Keithley gate setup in the
templates (output range, software ramp ``step``, hard-limit validator) so a
QDAC channel's ``dc_constant_V`` drops in wherever ``k.volt`` is used today.

The QDAC-II is a 24-channel ±10 V (±2 V low-range) precision source; it cannot
drive a high-voltage gate (e.g. a ±100 V Si gate stays on a Keithley 2410).
Because each channel reads its own current (``read_current_A``), a QDAC gate
feeds the generic ``sharpelab_nb.leakage.leakage_check`` directly (``station`` is
injected from the run-before context, so it is not passed in ``args``)::

    qd_bg = bring_up_qdac_gate(qdac.channel(2), limit=(-8, 8),
                               meas_range="low", meas_nplc=10)
    s.register_run_before(leakage_check,
                          args=(det, qd_bg.read_current_A, qd_bg.dc_constant_V))
"""
from __future__ import annotations

from qcodes import validators
from drivers.QDAC2 import QDac2, QDac2Channel

# ±V output ceiling per QDAC-II output range (manual §5.2.1: ±10 V / ±2 V).
_RANGE_CEILING = {"high": 10.0, "low": 2.0}


def bring_up_qdac_gate(
    channel: QDac2Channel,
    *,
    limit: tuple[float, float],
    step: float = 0.005,
    slew: float | None = None,
    output_range: str = "high",
    output_filter: str = "dc",
    meas_range: str | None = None,
    meas_nplc: int | None = None,
) -> QDac2Channel:
    """Configure a QDAC-II channel as a gate and return it.

    Sets the output range and (optionally) hardware slew, installs a hard
    voltage fence on ``dc_constant_V`` plus a software ramp ``step`` (matching
    the Keithley gate pattern, so ``sweep`` and the leakage interrupter see the
    same per-point cadence), and optionally configures the current-measurement
    range/integration used by ``read_current_A``. The returned channel exposes
    the gate voltage as ``channel.dc_constant_V`` and the leakage current as
    ``channel.read_current_A``.

    Args:
        channel: A connected ``QDac2`` channel (``qdac.ch01`` /
            ``qdac.channel(1)``).
        limit: ``(lo, hi)`` hard voltage fence (V). Must fit inside the selected
            ``output_range`` (±10 V high / ±2 V low) — the guardrail that
            refuses, e.g., a ±50 V Si-gate fence on the QDAC.
        step: Software ramp increment (V) installed on ``dc_constant_V.step``.
        slew: Hardware slew rate (V/s); ``None`` leaves the channel default.
        output_range: ``'high'`` (±10 V) or ``'low'`` (±2 V).
        output_filter: Output low-pass — ``'dc'`` / ``'med'`` / ``'high'``.
        meas_range: Current-measurement range ``'low'`` / ``'high'``; ``'low'``
            is QDevil's recommendation for leak detection. ``None`` leaves it.
        meas_nplc: Current-measurement integration (line cycles). ``None``
            leaves it.

    Returns:
        The same ``channel``, configured.
    """
    ceiling = _RANGE_CEILING[output_range]
    lo, hi = limit
    assert -ceiling <= lo <= hi <= ceiling, (
        f"gate limit {limit} does not fit the QDAC-II {output_range!r} output "
        f"range (±{ceiling} V)"
    )

    channel.output_range(output_range)
    channel.output_filter(output_filter)
    if slew is not None:
        channel.dc_slew_rate_V_per_s(slew)
    channel.dc_constant_V.step = step
    channel.dc_constant_V.vals = validators.Numbers(lo, hi)
    if meas_range is not None:
        channel.measurement_range(meas_range)
    if meas_nplc is not None:
        channel.measurement_nplc(meas_nplc)
    return channel
