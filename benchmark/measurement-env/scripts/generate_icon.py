"""Generate measurement-env icon: SR830 lock-in amplifier front panel."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = size // 16
    body = (pad, pad, size - pad, size - pad)

    # Main body — dark gray panel
    draw.rounded_rectangle(body, radius=size // 12, fill="#2a2a2e", outline="#1a1a1e", width=2)

    # Display window — dark screen with green glow
    disp_l = pad + size // 8
    disp_t = pad + size // 6
    disp_r = size - pad - size // 8
    disp_b = pad + size // 2 - size // 16
    draw.rounded_rectangle(
        (disp_l, disp_t, disp_r, disp_b),
        radius=size // 32,
        fill="#0a1a0a",
        outline="#333",
        width=1,
    )

    # Sine wave on display
    import math

    wave_cx = (disp_l + disp_r) // 2
    wave_cy = (disp_t + disp_b) // 2
    wave_w = disp_r - disp_l - size // 16
    wave_h = (disp_b - disp_t) // 3
    points = []
    for i in range(60):
        t = i / 59
        x = wave_cx - wave_w // 2 + int(t * wave_w)
        y = wave_cy - int(math.sin(t * 4 * math.pi) * wave_h)
        points.append((x, y))
    draw.line(points, fill="#00dd44", width=max(2, size // 80))

    # Readout text above wave
    try:
        font = ImageFont.truetype("arial.ttf", size // 14)
    except OSError:
        font = ImageFont.load_default()
    draw.text(
        (disp_l + size // 16, disp_t + size // 32),
        "1.234 mV",
        fill="#00cc33",
        font=font,
    )

    # Knobs row — three circles below the display
    knob_y = disp_b + (size - pad - disp_b) // 2
    knob_r = size // 14
    knob_colors = ["#555", "#555", "#555"]
    for i, color in enumerate(knob_colors):
        cx = disp_l + (i + 1) * (disp_r - disp_l) // 4
        draw.ellipse(
            (cx - knob_r, knob_y - knob_r, cx + knob_r, knob_y + knob_r),
            fill=color,
            outline="#333",
            width=1,
        )
        # Knob indicator line
        draw.line(
            (cx, knob_y - knob_r + 3, cx, knob_y - knob_r // 3),
            fill="#aaa",
            width=max(1, size // 100),
        )

    # Label at top
    try:
        label_font = ImageFont.truetype("arial.ttf", size // 18)
    except OSError:
        label_font = ImageFont.load_default()
    draw.text(
        (disp_l, pad + size // 32),
        "SR830",
        fill="#999",
        font=label_font,
    )

    # BNC connectors — small circles at bottom
    bnc_y = size - pad - size // 10
    bnc_r = size // 28
    for i in range(4):
        cx = disp_l + size // 12 + i * (disp_r - disp_l - size // 6) // 3
        draw.ellipse(
            (cx - bnc_r, bnc_y - bnc_r, cx + bnc_r, bnc_y + bnc_r),
            fill="#1a1a1e",
            outline="#666",
            width=1,
        )
        # Center pin
        draw.ellipse(
            (cx - 2, bnc_y - 2, cx + 2, bnc_y + 2),
            fill="#aa8833",
        )

    return img


def main():
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)

    img = generate(512)

    # Save as .ico with multiple sizes (render large, downsample for crispness)
    ico_sizes = [16, 32, 48, 64, 128, 256]
    ico_path = out / "measurement-env.ico"
    img.save(ico_path, format="ICO", sizes=[(s, s) for s in ico_sizes])
    print(f"Saved {ico_path} ({ico_path.stat().st_size} bytes)")

    # Also save PNG for reference
    png_path = out / "measurement-env.png"
    img.save(png_path)
    print(f"Saved {png_path}")


if __name__ == "__main__":
    main()
