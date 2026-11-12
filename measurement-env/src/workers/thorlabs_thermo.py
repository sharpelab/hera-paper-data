"""Thorlabs TSP01B temperature/humidity worker.

Stdout protocol:
    [init] ...          initialization diagnostics
    [ready]             signals successful first reading
    [data] {"_summary": "23.4C — Oh so chilly!", "temp": "23.4 C", "humidity": "42.1%"}
    [error] ...         non-fatal errors (InfluxDB write failures, etc.)

Reads config from toploader.toml in the repo root.
"""

import json
import sys
import time

import pyvisa

from core import Tag, emit
from core.config import load_config
from core.influx import setup_influx, write_point

MEASUREMENT = "thorlabs_thermo"
READ_INTERVAL = 60


def _connect_sensor():
    emit(Tag.INIT, "Scanning USB devices...")
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    emit(Tag.INIT, f"Found resources: {list(resources)}")

    usb_resource = None
    for resource in resources:
        if resource.startswith("USB"):
            usb_resource = resource
            break

    if usb_resource is None:
        emit(Tag.ERROR, "No USB device found")
        sys.exit(1)

    emit(Tag.INIT, f"Connecting to {usb_resource}")
    inst = rm.open_resource(usb_resource)
    return inst


def main():
    config = load_config()

    try:
        inst = _connect_sensor()
        _client, write_api, org, bucket = setup_influx(config.influxdb)
    except Exception as e:
        emit(Tag.ERROR, f"Startup failed: {e}")
        raise

    first = True
    while True:
        try:
            temp = float(inst.query("SENS1:TEMP:DATA?").strip())
            hum = float(inst.query("SENS2:HUM:DATA?").strip())
        except Exception as e:
            emit(Tag.ERROR, f"Sensor read failed: {e}")
            time.sleep(READ_INTERVAL)
            continue

        if first:
            emit(Tag.INIT, f"First reading: {temp} C, {hum}%")
            emit(Tag.READY)
            first = False

        vibe = "Wow so warm!" if temp > 23 else "Oh so chilly!"
        emit(Tag.DATA, json.dumps({
            "_summary": f"{temp:.1f}C — {vibe}",
            "temp": f"{temp:.1f} C",
            "humidity": f"{hum:.1f}%",
        }))

        try:
            write_point(write_api, org, bucket, MEASUREMENT, "temp", temp, "C")
            write_point(write_api, org, bucket, MEASUREMENT, "humidity", hum, "%")
        except Exception as e:
            emit(Tag.ERROR, f"InfluxDB write failed: {e}")

        time.sleep(READ_INTERVAL)


if __name__ == "__main__":
    main()
