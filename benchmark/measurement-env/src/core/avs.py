"""AVS-47B shared utilities."""

import time

import pyvisa as visa
from pyvisa.resources import MessageBasedResource

from . import Tag, emit


def wait_opc(avs: MessageBasedResource, timeout: int = 120) -> None:
    """Poll *OPC? until ready. Raises TimeoutError if exceeded."""
    start = time.monotonic()
    while True:
        if avs.query("*OPC?").strip() == "1":
            return
        if time.monotonic() - start > timeout:
            raise TimeoutError(f"*OPC? not ready after {timeout}s")
        time.sleep(1)


def connect_gpib(gpib_addr: str) -> tuple[visa.ResourceManager, MessageBasedResource]:
    """Open persistent GPIB connection. Returns (ResourceManager, resource)."""
    emit(Tag.INIT, f"GPIB: {gpib_addr}")
    rm = visa.ResourceManager()
    avs = rm.open_resource(gpib_addr)
    avs.clear()
    idn = avs.query("*IDN?").strip()
    emit(Tag.INIT, f"Connected: {idn}")
    return rm, avs


def format_temp(kelvin: float) -> str:
    """Format temperature for display (mK if < 1 K, else K)."""
    if kelvin <= 0:
        return "out of range"
    if kelvin < 1:
        return f"{kelvin * 1000:.1f} mK"
    return f"{kelvin:.3f} K"
