# Read-only check of the rotator-servo lock-ins' excitations.
for ch, role in [(sr830_6, "theta"), (sr830_7, "phi"), (sr830_1, "current-drive (ref)")]:
    try:
        amp = ch.amplitude()
        freq = ch.frequency()
        try:
            ref = ch.reference_source()
        except Exception:
            ref = "?"
        flag = "OFF (min)" if amp <= 0.0051 else ">>> EXCITATION ON <<<"
        print(f"{ch.name} ({role}): amplitude={amp*1e3:.1f} mV  freq={freq:.3f} Hz  ref={ref}   {flag}")
    except Exception as e:
        print(f"{ch.name} ({role}): read error -> {e!r}")
