"""
split_layers.py — turn ONE generated image into the three parallax layers
(back / middle / front) that the slider uses.

It does automatically what the original Basic3D PSDs did by hand:
  back   = the full image
  middle = everything nearer than the mid threshold (transparent above it)
  front  = only the nearest things (transparent everywhere else)

Depth comes from Depth Anything V2 (runs locally, first run downloads the model).

  pip install -r tools/requirements.txt

  python tools/split_layers.py tools/raw/frost.png --slide 1
  python tools/split_layers.py tools/raw/ember.png --slide 2 --mid 0.5 --front 0.8
  python tools/split_layers.py tools/raw/storm.png --slide 4 --preview

Tuning:
  --mid / --front  are quantiles of the depth map (0–1). Higher = fewer pixels
                   in that layer. Defaults 0.55 / 0.82 work for most landscapes.
  --feather        soft edge in px (default 4).
  --depth FILE     use your own depth map instead (white = near). Handy if you
                   want to paint a better one in Photoshop.
  --save-depth     also writes the estimated depth map next to the source
                   image, so you can refine it and feed it back with --depth.
  --preview        writes magenta-backed previews next to the source image.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

DEFAULT_MODEL = "depth-anything/Depth-Anything-V2-Small-hf"


def estimate_depth(img: Image.Image, model: str) -> np.ndarray:
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise SystemExit(
            "transformers is not installed. Run: pip install -r tools/requirements.txt\n"
            "or pass your own depth map with --depth depth.png"
        ) from exc
    pipe = pipeline("depth-estimation", model=model)
    depth = pipe(img)["depth"].convert("L").resize(img.size, Image.BICUBIC)
    return np.asarray(depth, dtype=np.float32) / 255.0


def load_depth(path: Path, size) -> np.ndarray:
    d = Image.open(path).convert("L").resize(size, Image.BICUBIC)
    return np.asarray(d, dtype=np.float32) / 255.0


def odd(n: int) -> int:
    n = max(1, int(n))
    return n if n % 2 else n + 1


def layer_mask(depth: np.ndarray, quantile: float, feather: float, grow: int) -> Image.Image:
    thr = float(np.quantile(depth, quantile))
    m = Image.fromarray(((depth >= thr) * 255).astype(np.uint8), "L")
    # opening then closing: drop specks, fill pin-holes
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    if grow > 0:
        m = m.filter(ImageFilter.MaxFilter(odd(grow * 2 + 1)))
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return m


def cutout(img: Image.Image, mask: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    rgba.putalpha(mask)
    return rgba


def preview(layer: Image.Image, path: Path) -> None:
    bg = Image.new("RGBA", layer.size, (255, 0, 255, 255))
    bg.alpha_composite(layer)
    bg.convert("RGB").resize((layer.width // 3, layer.height // 3)).save(path, quality=85)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path, help="generated 16:9 image (png/jpg/webp)")
    ap.add_argument("--slide", type=int, required=True, help="slide number 1-4")
    ap.add_argument("--out", type=Path, default=Path("public/img/slides"))
    ap.add_argument("--width", type=int, default=2400, help="output width in px (keeps 16:9)")
    ap.add_argument("--mid", type=float, default=0.55, help="depth quantile for the middle layer")
    ap.add_argument("--front", type=float, default=0.82, help="depth quantile for the front layer")
    ap.add_argument("--feather", type=float, default=4.0)
    ap.add_argument("--grow", type=int, default=1, help="expand masks by N px to hide halos")
    ap.add_argument("--depth", type=Path, help="use this depth map instead of estimating one")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--save-depth", action="store_true")
    ap.add_argument("--preview", action="store_true", help="also write magenta-backed previews")
    a = ap.parse_args()

    if not 0 < a.mid < a.front < 1:
        raise SystemExit("--mid must be smaller than --front, both between 0 and 1")

    img = Image.open(a.image).convert("RGB")
    if img.width > a.width:
        img = img.resize((a.width, round(img.height * a.width / img.width)), Image.LANCZOS)

    depth = load_depth(a.depth, img.size) if a.depth else estimate_depth(img, a.model)
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-6)

    a.out.mkdir(parents=True, exist_ok=True)
    stem = a.out / f"slide-{a.slide}-layer"

    img.save(f"{stem}-back.webp", "WEBP", quality=86, method=6)
    middle = cutout(img, layer_mask(depth, a.mid, a.feather, a.grow))
    front = cutout(img, layer_mask(depth, a.front, a.feather, a.grow))
    middle.save(f"{stem}-middle.webp", "WEBP", quality=88, method=6)
    front.save(f"{stem}-front.webp", "WEBP", quality=88, method=6)

    # depth maps and previews go next to the source image, never into public/
    side = a.image.parent
    if a.save_depth:
        Image.fromarray((depth * 255).astype(np.uint8)).save(side / f"slide-{a.slide}-depth.png")
    if a.preview:
        preview(middle, side / f"slide-{a.slide}-preview-middle.jpg")
        preview(front, side / f"slide-{a.slide}-preview-front.jpg")

    print(f"slide {a.slide}: back / middle / front written to {a.out}  ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
