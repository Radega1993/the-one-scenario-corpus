"""Preview rendering for map_space_saturation_v1 (matplotlib or Pillow fallback)."""

from __future__ import annotations

from pathlib import Path


def render_preview(roads_path: Path, preview_path: Path, world_size: tuple[int, int]) -> None:
    try:
        import matplotlib  # type: ignore

        matplotlib.use("Agg")
        _render_preview_matplotlib(roads_path, preview_path, world_size)
    except ModuleNotFoundError:
        render_preview_pil(roads_path, preview_path, world_size)


def _render_preview_matplotlib(roads_path: Path, preview_path: Path, world_size: tuple[int, int]) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from map_geometry import parse_linestrings, wkt_to_sim_coords

    raw = parse_linestrings(roads_path)
    sim = wkt_to_sim_coords(raw)
    wx, wy = world_size

    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")
    for line in sim:
        xs, ys = zip(*line)
        ax.plot(xs, ys, color="#2c5282", linewidth=0.5, alpha=0.9)
    if wx > 0 and wy > 0:
        ax.add_patch(Rectangle((0, 0), wx, wy, fill=False, edgecolor="#a0aec0", linestyle="--", linewidth=1))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(preview_path, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def render_preview_pil(roads_path: Path, preview_path: Path, world_size: tuple[int, int]) -> None:
    from PIL import Image, ImageDraw

    from map_geometry import parse_linestrings, wkt_to_sim_coords

    raw = parse_linestrings(roads_path)
    sim = wkt_to_sim_coords(raw)

    img_w, img_h = 900, 650
    margin = 15
    wx, wy = world_size
    scale_x = (img_w - 2 * margin) / float(wx) if wx > 0 else 1.0
    scale_y = (img_h - 2 * margin) / float(wy) if wy > 0 else 1.0
    scale = min(scale_x, scale_y)

    img = Image.new("RGB", (img_w, img_h), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    if wx > 0 and wy > 0:
        x0 = margin
        y0 = img_h - margin
        x1 = margin + wx * scale
        y1 = img_h - margin - wy * scale
        draw.rectangle([x0, y1, x1, y0], outline=(160, 174, 192), width=2)

    for line in sim:
        pts = []
        for x, y in line:
            px = margin + x * scale
            py = (img_h - margin) - y * scale
            pts.append((px, py))
        if len(pts) >= 2:
            draw.line(pts, fill=(44, 82, 130), width=2)

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(preview_path)
