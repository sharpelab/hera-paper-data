"""InfluxDB helpers."""

from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from . import Tag, emit
from .config import InfluxConfig


def setup_influx(
    cfg: InfluxConfig, *, timeout: int = 60_000,
) -> tuple[InfluxDBClient, WriteApi, str, str]:
    """Create InfluxDB client and write API from config.

    Returns (client, write_api, org, bucket).
    """
    emit(Tag.INIT, f"InfluxDB: {cfg.url} org={cfg.org} bucket={cfg.bucket}")
    client = InfluxDBClient(url=cfg.url, token=cfg.token, org=cfg.org, timeout=timeout)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    return client, write_api, cfg.org, cfg.bucket


def write_point(
    write_api: WriteApi,
    org: str,
    bucket: str,
    measurement: str,
    metric: str,
    value: float,
    unit: str,
    *,
    timestamp: datetime | None = None,
) -> None:
    """Write a single metric point to InfluxDB."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    point = (
        Point(measurement)
        .tag("metric", metric)
        .tag("unit", unit)
        .field("value", float(value))
        .time(timestamp, WritePrecision.NS)
    )
    write_api.write(bucket=bucket, org=org, record=point)
