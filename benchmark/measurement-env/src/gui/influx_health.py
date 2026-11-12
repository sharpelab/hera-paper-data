"""InfluxDB freshness checks for launcher health panels.

A worker owning several instruments guards one metric per instrument, and its
panel is healthy only while every one of them is being written. An instrument
that stops publishing yields no rows rather than an old row, so staleness has
no server-side aggregate that can spot it — the client compares the names it
asked for against the names that came back.
"""

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def _age_str(seconds: float) -> str:
    """Format an age in seconds as a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    return f"{int(seconds // 3600)}h ago"


def _format_write(when: datetime) -> str:
    """Local clock time plus age, e.g. '16:52:55 (10s ago)'."""
    age = (datetime.now(timezone.utc) - when).total_seconds()
    return f"{when.astimezone().strftime('%H:%M:%S')} ({_age_str(age)})"


def _metric_filter(metrics: tuple[str, ...]) -> str:
    """Build Flux filter expression."""
    names = ", ".join(f'"{m}"' for m in metrics)
    return f"contains(value: r.metric, set: [{names}])"


@dataclass(frozen=True)
class HealthDisplay:
    """What a panel renders for its InfluxDB row.

    `text` is the label; `summary` is the same state said briefly, for the
    launcher's aggregate issue list, which has the panel beside it already
    and does not need the clock time repeated.
    """
    text: str
    summary: str
    ok: bool


def _parse_last_writes(body: str) -> dict[str, datetime]:
    """Parse an InfluxDB CSV response into {metric: last write}.

    Only metrics that had rows appear. Column positions come from the CSV
    header rather than fixed indices: the response carries both _time and
    metric, and their order is the server's to choose. A second header
    (schema change mid-body) re-seats them.
    """
    out: dict[str, datetime] = {}
    time_col: int | None = None
    metric_col: int | None = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip("\r")
        if not line or line.startswith("#"):
            continue
        parts = line.split(",")

        if "_time" in parts and "metric" in parts:
            time_col = parts.index("_time")
            metric_col = parts.index("metric")
            continue
        if time_col is None or metric_col is None:
            continue
        if len(parts) <= time_col or len(parts) <= metric_col:
            continue

        ts, name = parts[time_col], parts[metric_col]
        if not ts or not name:
            continue
        when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if name not in out or when > out[name]:
            out[name] = when

    return out


def fetch_last_writes(
    url: str,
    token: str,
    org: str,
    bucket: str,
    measurement: str,
    metrics: tuple[str, ...],
    window_seconds: int,
) -> dict[str, datetime | None]:
    """Query InfluxDB for the last write of each metric.

    Returns one entry per requested metric — None where it had no write in
    the window, which is the only way a dark instrument shows up. Freshness
    is not judged here; that needs the threshold, which the poller owns.
    """
    metrics = tuple(metrics)
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -{window_seconds}s)
      |> filter(fn: (r) => r._measurement == "{measurement}" and {_metric_filter(metrics)})
      |> group(columns: ["metric"])
      |> last()
      |> keep(columns: ["_time", "metric"])
    '''
    req = Request(
        f"{url.rstrip('/')}/api/v2/query?org={org}",
        data=query.encode(),
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/vnd.flux",
            "Accept": "text/csv",
        },
    )
    resp = urlopen(req, timeout=10)
    seen = _parse_last_writes(resp.read().decode())
    return {m: seen.get(m) for m in metrics}


class InfluxHealthPoller:
    """Background poller for InfluxDB metric freshness.

    Runs a daemon thread that calls fetch_last_writes() on interval. Results
    are stored as plain attributes — no Qt, no locks. The poller owns
    the threshold, so it sets the query window, judges staleness, and derives
    what the panels render.
    """

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        measurement: str,
        metrics: tuple[str, ...],
        threshold_seconds: int,
        poll_interval: float = 5.0,
    ) -> None:
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket
        self._measurement = measurement
        self.metrics = tuple(metrics)
        self.threshold_seconds = threshold_seconds
        self._poll_interval = poll_interval

        self._stop_event = threading.Event()
        self._running = False

        self.last_writes: dict[str, datetime | None] = {m: None for m in self.metrics}
        self.error: str | None = None

    def _stale(self, writes: dict[str, datetime | None]) -> list[str]:
        """Metrics in `writes` failing the threshold, in config order."""
        now = datetime.now(timezone.utc)
        stale = []
        for m in self.metrics:
            when = writes.get(m)
            if when is None or (now - when).total_seconds() >= self.threshold_seconds:
                stale.append(m)
        return stale

    @property
    def stale_metrics(self) -> list[str]:
        """Metrics failing the threshold, in config order. Empty means healthy."""
        return self._stale(self.last_writes)

    @property
    def fresh(self) -> bool:
        return not self.stale_metrics

    def display(self) -> HealthDisplay:
        """Derive the panel's label and health, toolkit-neutrally.

        One derivation for every panel: each sets its
        label to the text and colours it on the flag.
        """
        if self.error is not None:
            return HealthDisplay("error", "error", False)

        # One read: the poll thread swaps the dict wholesale, so every
        # judgement below must come from the same snapshot.
        writes = self.last_writes
        stale = self._stale(writes)
        if not stale:
            return HealthDisplay(
                _format_write(max(w for w in writes.values() if w is not None)), "", True,
            )

        names = ", ".join(stale)
        known = [w for w in (writes.get(m) for m in stale) if w is not None]
        if not known:
            return HealthDisplay(f"no data: {names}", f"no data: {names}", False)
        # Dated from the oldest stale metric: a stale panel must never show
        # an age borrowed from the metrics that are still healthy.
        return HealthDisplay(
            f"{_format_write(min(known))} — stale: {names}", f"stale: {names}", False,
        )

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        try:
            while True:
                try:
                    self.last_writes = fetch_last_writes(
                        self._url, self._token, self._org, self._bucket,
                        self._measurement, self.metrics,
                        self.threshold_seconds * 2,
                    )
                    self.error = None
                except Exception as e:
                    self.error = str(e)

                if self._stop_event.wait(self._poll_interval):
                    break
        finally:
            self._running = False
