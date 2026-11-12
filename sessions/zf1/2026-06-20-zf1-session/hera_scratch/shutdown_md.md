## HERA — session shutdown / safe park

Park the device safely: **DC bias → 0** (device-card rule, first), AC excitation → minimum (un-drive the cold device), **k_tg & k_bg → 0 V**, **magnet → 0 T**. Reads everything back and asserts gates and magnet are at zero. `k_tg2` (rotator θ-winding, blocklisted/unused this session) is left untouched. Kernel and launcher workers stay up (no restart). ~30 s (gate ramps from ~0 are short; magnet already at nominal zero).
