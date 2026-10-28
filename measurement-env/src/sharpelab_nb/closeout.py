"""Session close-out — the last cell of a measurement notebook.

:func:`read_state` is called at bring-up to capture a restorable snapshot of
acquisition + gate state. :func:`close_out` is authored at session end to
replay that snapshot, step down excitation/heaters/gates in a fixed order,
park the mux, and land the field where the session brief says it should
land — either an explicit target or a deliberate "hold". The field endpoint
is never inferred from a restore: it's the one decision a close-out cell
always has to make explicitly.
"""
from typing import Any, Callable

from qcodes.parameters import Parameter

StageItem = tuple[Parameter, Any] | tuple[str, Callable[[], None]]


class StateRecord:
    """An ordered, read-only snapshot of ``(name, param, value)`` triples.

    Built by :func:`read_state`; consumed by ``close_out(restore=...)``.
    """

    def __init__(self, entries: list[tuple[str, Parameter, Any]]) -> None:
        self._entries = list(entries)

    def items(self) -> list[tuple[str, Parameter, Any]]:
        return list(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, param: Parameter) -> bool:
        return any(p is param for _, p, _ in self._entries)

    def __repr__(self) -> str:
        return "\n".join(f"{name} : {value}" for name, _, value in self._entries)


def read_state(**params: Parameter) -> StateRecord:
    """Read a curated set of parameters, print a ``name : value`` table, and
    return them as a :class:`StateRecord` for later ``close_out(restore=...)``.

    Kwarg order is preserved and is the order ``close_out`` replays in.
    """
    entries: list[tuple[str, Parameter, Any]] = []
    for name, param in params.items():
        value = param()
        entries.append((name, param, value))
        print(f"{name} : {value}")
    return StateRecord(entries)


def _validator_suffix(param: Parameter) -> str:
    vals = getattr(param, "vals", None)
    return f"  {vals!r}" if vals is not None else ""


def _readback_line(
    name: str | None,
    param: Parameter,
    *,
    setpoint: Any = None,
    has_setpoint: bool = False,
) -> str:
    label = name if name is not None else param.full_name
    try:
        value = param()
        note = ""
    except Exception:
        if not has_setpoint:
            raise
        value = setpoint
        note = "  (setpoint — no readback)"
    return f"{label} : {value}{note}{_validator_suffix(param)}"


def _check_field_not_side_effected(
    field_param: Parameter,
    restore: StateRecord | None,
    stages: list[list[StageItem] | None],
) -> None:
    if restore is not None and field_param in restore:
        raise ValueError(
            "field param appears in restore — the field endpoint is an "
            "explicit decision, never replayed as a side effect"
        )
    for stage in stages:
        if not stage:
            continue
        for first, _ in stage:
            if not isinstance(first, str) and first is field_param:
                raise ValueError(
                    "field param appears in a stage list — the field "
                    "endpoint is an explicit decision, never set as a "
                    "side effect"
                )


def _run_stage(
    stage_name: str,
    stage: list[StageItem] | None,
    touched: list[tuple[str | None, Parameter, Any]],
    seen: set[int],
) -> None:
    if not stage:
        return
    print(f"-- {stage_name}")
    for first, second in stage:
        if isinstance(first, str):
            label, fn = first, second
            print(f"   {label}")
            fn()
        else:
            param, value = first, second
            param(value)
            if id(param) not in seen:
                seen.add(id(param))
                touched.append((None, param, value))


def close_out(
    field: tuple[Parameter, float | str],
    *,
    restore: StateRecord | None = None,
    excitation: list[StageItem] | None = None,
    heaters: list[StageItem] | None = None,
    gates: list[StageItem] | None = None,
    mux: Any | None = None,
    extra_readback: dict[str, Parameter] | None = None,
) -> None:
    """Wind a session down: replay a restore, step down excitation/heaters/
    gates, park the mux, then land the field — an explicit target or a
    deliberate ``"hold"`` — and print a full readback.

    Args:
        field: ``(field_param, target)``. ``target`` is a float setpoint or
            the literal string ``"hold"``. Required — the field endpoint is
            never defaulted.
        restore: A :class:`StateRecord` from an earlier ``read_state()``,
            replayed via plain ``param(value)`` sets in capture order.
        excitation: Stage items, each either ``(param, value)`` or
            ``(label, fn)`` for a zero-arg callable (e.g. rig-specific
            heater-range-off oddities).
        heaters: Same shape as ``excitation``.
        gates: Same shape as ``excitation``.
        mux: If given, ``mux.park()`` is called between ``gates`` and the
            field endpoint.
        extra_readback: Read-only params appended to the final readback,
            beyond whatever was touched above.
    """
    field_param, target = field
    stages = [excitation, heaters, gates]
    _check_field_not_side_effected(field_param, restore, stages)

    touched: list[tuple[str | None, Parameter, Any]] = []
    seen: set[int] = set()

    if restore is not None:
        print(f"-- restore ({len(restore)} params)")
        for name, param, value in restore.items():
            param(value)
            if id(param) not in seen:
                seen.add(id(param))
                touched.append((name, param, value))

    _run_stage("excitation", excitation, touched, seen)
    _run_stage("heaters", heaters, touched, seen)
    _run_stage("gates", gates, touched, seen)

    if mux is not None:
        print("-- mux.park()")
        mux.park()

    holding = target == "hold"
    if holding:
        print("-- field: hold")
        held_value = field_param()
    else:
        print(f"-- field -> {target}")
        field_param(target)

    print()
    print("--- close-out readback ---")
    for name, param, value in touched:
        print(_readback_line(name, param, setpoint=value, has_setpoint=True))

    if holding:
        line = f'FIELD HELD at {held_value} T — deliberate ("hold")'
        print(line + _validator_suffix(field_param))
    else:
        # Read-truth: report the measured field, never the setpoint.
        print(f"field : {field_param()} T" + _validator_suffix(field_param))

    if extra_readback:
        for name, param in extra_readback.items():
            print(_readback_line(name, param))
