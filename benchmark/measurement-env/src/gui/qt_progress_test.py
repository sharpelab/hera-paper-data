from typing import Any

from gui.qt_progress import QtProgress, _Action


class _Rec:
    def __init__(self) -> None:
        self.msgs: list[dict[str, Any]] = []

    def send(self, msg: dict[str, Any]) -> None:
        self.msgs.append(msg)


class _Proc:
    def __init__(self) -> None:
        self.alive = False

    def start(self) -> None:
        self.alive = True

    def is_alive(self) -> bool:
        return self.alive


class _Ctx:
    def __init__(self) -> None:
        self.pipes: list[_Rec] = []

    def Pipe(self) -> tuple[_Rec, None]:
        r = _Rec()
        self.pipes.append(r)
        return r, None

    def Process(self, **kwargs: Any) -> _Proc:
        return _Proc()


def test_iteration_passes_through_without_window() -> None:
    # With no live window/pipe the factory must still yield every item.
    p = QtProgress()
    p._ensure = lambda: None  # type: ignore[method-assign]
    assert list(p(range(20))) == list(range(20))


def test_total_falls_back_when_no_len() -> None:
    p = QtProgress()
    p._ensure = lambda: None  # type: ignore[method-assign]
    assert list(p(iter(range(5)))) == list(range(5))


def test_failsoft_on_broken_pipe() -> None:
    # A dead/closed window (send raises) must not break the loop, and the
    # handle is dropped so the next sweep relaunches.
    p = QtProgress()

    class _BrokenPipe:
        def send(self, msg: Any) -> None:
            raise BrokenPipeError

    p._ensure = lambda: None  # type: ignore[method-assign]
    p._pipe = _BrokenPipe()  # type: ignore[assignment]
    assert list(p(range(10), position=1, leave=False)) == list(range(10))
    assert p._pipe is None


def test_relaunch_replays_in_flight_bars() -> None:
    # When the window dies mid-sweep, the relaunched window must be rebuilt
    # with the bars still in flight (regression: outer bar showed bare "n"
    # with an unfilled bar because its START went to the dead window).
    p = QtProgress()
    p._ctx = _Ctx()  # type: ignore[assignment]

    outer = p(range(3), position=0, total=3)
    next(outer)  # spawns window 0, sends START(pos0)
    p._active[0]["n"] = 2  # outer has advanced
    p._proc.alive = False  # operator closed the window

    inner = p(range(4), position=1, total=4)
    next(inner)  # _ensure() relaunches -> must replay pos0 before START(pos1)

    relaunched = p._ctx.pipes[1].msgs  # type: ignore[attr-defined]
    start0 = [m for m in relaunched if m["action"] is _Action.START and m["position"] == 0]
    upd0 = [m for m in relaunched if m["action"] is _Action.UPDATE and m["position"] == 0]
    start1 = [m for m in relaunched if m["action"] is _Action.START and m["position"] == 1]
    assert start0 and start0[0]["total"] == 3
    assert upd0 and upd0[0]["n"] == 2
    assert start1
    assert relaunched.index(start0[0]) < relaunched.index(start1[0])
