"""Streaming gate-leakage interrupter — a causal dI/dV CUSUM detector.

Used as a live abort during a continuous outward gate push: it watches the
gate-current channel and trips the sweep the moment the current departs
super-linearly from its flat baseline (the *foot* of the leakage upturn) — earlier
and more reproducibly than a human watching the live plot.

Two layers:

- :class:`LeakageDetector` — the pure, instrument-agnostic algorithm. Feed it
  ``(V, I)`` per point via :meth:`~LeakageDetector.update`; it self-calibrates and
  trips. :func:`leakage_check` (``register_run_before``, re-reads the SMU each point)
  and :func:`leakage_check_after` (``register_run_after``, zero extra reads — feeds the
  detector the values the sweep already measured) are the low-level adapters.
- :func:`k2400_leakage_guard` — the pit-of-success wrapper for a Keithley 2400 (the
  survey is always run on a 2400). A context manager that configures the SMU
  (integration, averaging, pA range), yields a bound guard, and restores the SMU on
  exit, so the caller just hands over the instrument.

How the algorithm works, per point fed to :meth:`LeakageDetector.update`:

1. causal-median-filter the current (rejects per-point spikes and smooths in one step),
2. calibrate a baseline line ``b0`` + noise ``sigma_I`` from the first safe stretch of
   the push (``|V| <= base_V``),
3. run a CUSUM on the local slope-excess z-score — how far the local ``dI/dV`` sits
   above ``b0``, in units of the local slope noise — resetting on dips.

A violent runaway crosses the alarm bound ``H`` in 1-2 points; a gentle upturn after
several; transient noise never accumulates. No tail-confirmation: live, a false abort
is cheap (restart the sweep) and a missed leak is expensive (dead device), so it
commits forward. It assumes **one continuous push from parked-safe** — a chunked
sweep's per-segment DC offset steps fake a sloped baseline and false-trip it.

The default ``(slack, H)`` and the inset applied to the reported onset are
**heuristics** (n=1 device, QC0426 replay); tune them against a live continuous push.
See ``hera/recipes/device-init/gate-leakage-survey.md``.
"""
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Protocol

import numpy as np

_K = 1.4826  # MAD -> sigma for normal noise


class _Interruptible(Protocol):
    interrupt_requested: bool


class LeakageDetector:
    """Causal, self-calibrating dI/dV CUSUM leakage detector for a continuous push.

    Feed it ``(V, I)`` per sweep point via :meth:`update`. After it has calibrated a
    baseline from the first safe stretch (``|V| <= base_V``), each point updates a CUSUM
    on the local slope-excess z-score; ``update`` returns ``True`` once the CUSUM crosses
    ``H`` (the trip), and :attr:`trip_V` holds the foot voltage where the accumulation
    began.

    Args:
        base_V: Calibrate the baseline from points within this ``|V|`` of 0 (the safe
            start of the push).
        min_base: Minimum baseline points before calibrating.
        skip: Drop this many leading points (settling) from the baseline fit.
        win_V: Trailing-window half-width (volts) for the local ``dI/dV`` fit.
        sm_win: Causal median-filter window (points).
        slack: CUSUM slack in slope-sigmas — drift below this does not accumulate.
        H: CUSUM alarm bound; the gate trips when the accumulator exceeds it.
    """

    def __init__(
        self,
        base_V: float = 2.5,
        min_base: int = 10,
        skip: int = 3,
        win_V: float = 0.4,
        sm_win: int = 5,
        slack: float = 4.0,
        H: float = 12.0,
    ) -> None:
        self.base_V, self.min_base, self.skip = base_V, min_base, skip
        self.win_V, self.sm_win = win_V, sm_win
        self.slack, self.H = slack, H
        self.V: list[float] = []
        self.Iraw: list[float] = []
        self.Ism: list[float] = []
        self.b0: float | None = None
        self.sigma_I: float | None = None
        self.S = 0.0
        self.last_z = 0.0
        self.run_start: float | None = None
        self.tripped = False
        self.trip_V: float | None = None

    def update(self, V: float, I: float) -> bool:
        """Feed one sweep point. Returns ``True`` once tripped (=> request interrupt)."""
        if self.tripped:
            return True
        self.V.append(V)
        self.Iraw.append(I)
        # causal median filter: rejects spikes and smooths in one step
        n = len(self.Iraw)
        self.Ism.append(float(np.median(self.Iraw[max(0, n - self.sm_win):n])))
        Va = np.array(self.V)
        Ia = np.array(self.Ism)

        # calibrate baseline once we've pushed past base_V with enough safe points
        if self.b0 is None:
            base = np.abs(Va) <= self.base_V
            if abs(V) > self.base_V and base.sum() >= self.min_base:
                Vb, Ib = Va[base][self.skip:], Ia[base][self.skip:]
                self.b0, a = np.polyfit(Vb, Ib, 1)
                resid = Ib - (a + self.b0 * Vb)
                self.sigma_I = max(_K * np.median(np.abs(resid - np.median(resid))), 1e-13)
            return False
        assert self.sigma_I is not None

        # local slope over the trailing win_V window (buffer is all past/outward pts)
        sel = np.abs(Va - V) <= self.win_V
        Vw, Iw = Va[sel], Ia[sel]
        if len(Vw) < 4 or np.ptp(Vw) == 0:
            return False
        cf = np.polyfit(Vw, Iw, 1)
        resid = Iw - np.polyval(cf, Vw)
        # LOCAL noise, floored by baseline noise: a noisy stretch inflates this so z
        # shrinks (no false trip); a clean rising stretch keeps z high.
        sigma_loc = max(_K * np.median(np.abs(resid - np.median(resid))), self.sigma_I)
        se = sigma_loc / np.sqrt(np.sum((Vw - Vw.mean()) ** 2))
        self.last_z = (cf[0] - self.b0) / se  # slope-excess in sigmas (leak => +)

        if self.S <= 0:
            self.run_start = V
        self.S = max(0.0, self.S + self.last_z - self.slack)
        if self.S > self.H:
            self.tripped = True
            self.trip_V = self.run_start  # foot = where accumulation began
            return True
        return False


def leakage_check(
    detector: LeakageDetector,
    curr_param: Callable[[], float],
    volt_param: Callable[[], float],
    station: _Interruptible,
) -> None:
    """Low-level ``register_run_before`` adapter — re-reads the SMU each point.

    ``station`` is injected from the run-before context, so register with the *other*
    args only; passing ``station`` in ``args`` too double-binds it
    (``TypeError: got multiple values for argument 'station'``). For a Keithley 2400,
    prefer :func:`k2400_leakage_guard`, which wires this up and configures the
    instrument for you. Use this directly only for a non-2400 source::

        s.register_run_before(leakage_check, args=(detector, gate.curr, gate.volt))

    For zero extra instrument reads, prefer :func:`leakage_check_after`.
    """
    if detector.update(volt_param(), curr_param()):
        station.interrupt_requested = True


def leakage_check_after(
    detector: LeakageDetector,
    station: _Interruptible,
    data: list[float],
    *,
    i_col: int = 2,
    v_col: int = 1,
) -> None:
    """Low-level ``register_run_after`` adapter — **zero** extra instrument reads.

    Instead of re-reading the SMU, it feeds the detector what the sweep already
    measured. The run-after ``data`` row is ``[time, setpoint, *followed_params]``, so
    ``v_col=1`` is the commanded gate voltage and ``i_col`` is the gate-current
    followed-param column. ``station``/``data`` are injected from the run-after
    context, so register with the detector only::

        s.register_run_after(leakage_check_after, args=(detector,))      # i_col=2
        # gate current is not the first followed param -> pin its column:
        s.register_run_after(partial(leakage_check_after, i_col=N), args=(detector,))

    Correctness conditions (not optional notes):

    - The **gate current must be a followed param**; ``i_col = 2 + its fp position``
      (2 if it is the first/only followed param).
    - ``data[i_col]`` is **gain-divided** (the station stores ``p() / gain``) — follow
      the gate-current param with ``gain=1`` so the detector sees the true current.
    - **V = setpoint** is exact and noise-free; for a voltage source it equals
      ``volt()``.
    - This aborts **one point past** the foot (vs ``run_before``'s one-before) — a
      single-point overshoot, acceptable under "false abort cheap, missed leak
      expensive".
    - Net vs the re-reading guard: **3 reads/pt -> 1 (~3x faster), identical detection.**
    """
    if detector.update(float(data[v_col]), float(data[i_col])):
        station.interrupt_requested = True


class _K2400Guard:
    """The bound guard yielded by :func:`k2400_leakage_guard`."""

    def __init__(self, detector: LeakageDetector, k: Any) -> None:
        self._detector = detector
        self._k = k

    def check(self, station: _Interruptible) -> None:
        """Register as ``s.register_run_before(guard.check, args=())`` — ``station``
        comes from the run-before context, so do *not* also pass it in ``args``.

        Re-reads the SMU each point (``volt()`` + ``curr()``); for zero extra reads use
        :meth:`check_after`.
        """
        if self._detector.update(float(self._k.volt()), float(self._k.curr())):
            station.interrupt_requested = True

    def check_after(
        self,
        station: _Interruptible,
        data: list[float],
        *,
        i_col: int = 2,
        v_col: int = 1,
    ) -> None:
        """``register_run_after`` form — **zero** extra instrument reads.

        Feeds the detector ``V = setpoint`` (``data[v_col]``) and ``I`` = the measured
        gate-current followed-param (``data[i_col]``, which must be followed with
        ``gain=1`` so it is the true current). Register with ``args=()``; pin a
        non-default current column via :func:`functools.partial`::

            s.register_run_after(guard.check_after, args=())                    # i_col=2
            s.register_run_after(partial(guard.check_after, i_col=N), args=())  # else

        See :func:`leakage_check_after` for the full correctness conditions.
        """
        if self._detector.update(float(data[v_col]), float(data[i_col])):
            station.interrupt_requested = True

    @property
    def detector(self) -> LeakageDetector:
        return self._detector

    @property
    def tripped(self) -> bool:
        return self._detector.tripped

    @property
    def trip_V(self) -> float | None:
        return self._detector.trip_V


@contextmanager
def k2400_leakage_guard(
    k: Any,
    *,
    nplc: int = 10,
    avg_n: int | None = 6,
    rangei: float | None = 1e-9,
    slack: float = 4.0,
    H: float = 12.0,
) -> Iterator[_K2400Guard]:
    """Configure a Keithley 2400 for a leakage survey, yield a guard, restore on exit.

    The survey is always run on a 2400, so this bakes in the good setup (pA current
    range, high integration, repeat-averaging) and pulls ``curr``/``volt`` off the
    instrument — the caller can't wire the wrong channel or forget to restore::

        with k2400_leakage_guard(k_bg) as guard:
            s.register_run_after(guard.check_after, args=())   # zero extra reads
            try:
                s.sweep(k_bg.volt, ramp, delay=delay)
            finally:
                s.ramp(k_bg.volt, 0)
        print(guard.trip_V)            # k_bg restored here

    Args:
        k: A qcodes Keithley 2400 instrument.
        nplc: Current-channel integration (``nplci``); 10 is the 2400 max.
        avg_n: Repeat-average filter count (1-100), or ``None`` to leave the filter
            untouched. The 2400 averaging filter has no qcodes parameter, so this is
            set via raw SCPI. **[BETA] verify the SCPI on the instrument.**
        rangei: Current range to force (pA-resolution default), or ``None`` to leave it.
        slack, H: :class:`LeakageDetector` CUSUM knobs.
    """
    saved_nplc = k.nplci()
    saved_rangei = k.rangei() if rangei is not None else None
    saved_count = k.ask("SENS:AVER:COUNT?") if avg_n is not None else None
    saved_state = k.ask("SENS:AVER:STATE?") if avg_n is not None else None

    k.nplci(nplc)
    if rangei is not None:
        k.rangei(rangei)
    if avg_n is not None:
        k.write("SENS:AVER:TCON REP")
        k.write(f"SENS:AVER:COUNT {int(avg_n)}")
        k.write("SENS:AVER:STATE ON")

    try:
        yield _K2400Guard(LeakageDetector(slack=slack, H=H), k)
    finally:
        k.nplci(saved_nplc)
        if rangei is not None:
            k.rangei(saved_rangei)
        if avg_n is not None:
            k.write(f"SENS:AVER:COUNT {saved_count}")
            k.write(f"SENS:AVER:STATE {saved_state}")
