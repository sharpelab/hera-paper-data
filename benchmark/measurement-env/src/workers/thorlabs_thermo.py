"""Thorlabs TSP01B temperature/humidity worker.

Stdout protocol (owned by core.poller):
    [init] ...          initialization diagnostics
    [waiting]           connected, waiting for first read
    [ready]             signals successful first reading
    [data] {"_summary": "23.4C — Oh so chilly!", "temp": "23.4 C", "humidity": "42.1%"}
    [error] ...         non-fatal errors (InfluxDB write failures, etc.)

Reads config from toploader.toml in the repo root.
"""

import pyvisa

from core import Tag, emit
from core.config import load_config
from core.influx import setup_influx, write_point
from core.poller import run

MEASUREMENT = "thorlabs_thermo"
READ_INTERVAL = 60


class Thermometer:
    """TSP01B temperature/humidity probe on the USB (VISA) bus."""

    name = "TSP01B"

    def __init__(self):
        self._rm = None
        self._inst = None

    def connect(self) -> None:
        emit(Tag.INIT, "Scanning USB devices...")
        self._rm = pyvisa.ResourceManager()
        resources = self._rm.list_resources()
        emit(Tag.INIT, f"Found resources: {list(resources)}")

        usb_resource = None
        for resource in resources:
            if resource.startswith("USB"):
                usb_resource = resource
                break

        if usb_resource is None:
            raise RuntimeError("No USB device found")

        emit(Tag.INIT, f"Connecting to {usb_resource}")
        self._inst = self._rm.open_resource(usb_resource)

    def close(self) -> None:
        try:
            self._inst.close()
        except Exception as e:
            emit(Tag.ERROR, f"TSP01B close failed: {e}")
        self._inst = None

    def read(self) -> tuple[float, float]:
        temp = float(self._inst.query("SENS1:TEMP:DATA?").strip())
        hum = float(self._inst.query("SENS2:HUM:DATA?").strip())
        return temp, hum


def make_publish(write_api, org, bucket):
    """Build the ((temp, humidity), cycle) -> [data] payload callable."""

    def publish(readings: tuple[float, float], cycle: int) -> dict[str, object]:
        temp, hum = readings
        if cycle == 0:
            emit(Tag.INIT, f"First reading: {temp} C, {hum}%")

        try:
            write_point(write_api, org, bucket, MEASUREMENT, "temp", temp, "C")
            write_point(write_api, org, bucket, MEASUREMENT, "humidity", hum, "%")
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")

        vibe = "Wow so warm!" if temp > 23 else "Oh so chilly!"
        return {
            "_summary": f"{temp:.1f}C — {vibe}",
            "temp": f"{temp:.1f} C",
            "humidity": f"{hum:.1f}%",
        }

    return publish


def main():
    try:
        config = load_config()
        _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    run(
        Thermometer(),
        interval=READ_INTERVAL,
        publish=make_publish(write_api, org, bucket),
    )


if __name__ == "__main__":
    main()
