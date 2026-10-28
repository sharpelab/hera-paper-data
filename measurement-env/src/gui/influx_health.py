"""InfluxDB freshness checker for launcher health panels."""

import threading
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def _metric_filter(metric: str) -> str:
    """Build Flux filter expression. Supports regex (e.g. /^P[12]_/)."""
    if metric.startswith("/"):
        return f"r.metric =~ {metric}"
    return f'r.metric == "{metric}"'


def check_freshness(
    url: str,
    token: str,
    org: str,
    bucket: str,
    measurement: str,
    metric: str,
    threshold_seconds: int,
) -> tuple[bool, datetime | None]:
    """Query InfluxDB for the last write of a metric.

    Returns (fresh, last_write) where fresh is True if the last write
    is within threshold_seconds of now.
    """
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -{threshold_seconds * 2}s)
      |> filter(fn: (r) => r._measurement == "{measurement}" and {_metric_filter(metric)})
      |> group()
      |> last()
      |> keep(columns: ["_time"])
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
    body = resp.read().decode()

    for line in body.strip().splitlines():
        if line.startswith(",_result"):
            parts = line.split(",")
            ts_str = parts[3]
            last_write = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - last_write).total_seconds()
            return age < threshold_seconds, last_write

    return False, None


class InfluxHealthPoller:
    """Background poller for InfluxDB metric freshness.

    Runs a daemon thread that calls check_freshness() on interval.
    Results are stored as plain attributes — no tkinter, no locks.
    """

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        measurement: str,
        metric: str,
        threshold_seconds: int,
        poll_interval: float = 5.0,
    ) -> None:
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket
        self._measurement = measurement
        self._metric = metric
        self.threshold_seconds = threshold_seconds
        self._poll_interval = poll_interval

        self._stop_event = threading.Event()
        self._running = False

        self.last_write: datetime | None = None
        self.error: str | None = None

    @property
    def fresh(self) -> bool:
        lw = self.last_write
        if lw is None:
            return False
        age = (datetime.now(timezone.utc) - lw).total_seconds()
        return age < self.threshold_seconds

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
                    _, last_write = check_freshness(
                        self._url, self._token, self._org, self._bucket,
                        self._measurement, self._metric, self.threshold_seconds,
                    )
                    self.last_write = last_write
                    self.error = None
                except Exception as e:
                    self.error = str(e)

                if self._stop_event.wait(self._poll_interval):
                    break
        finally:
            self._running = False
