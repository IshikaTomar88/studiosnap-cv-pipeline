"""
image_fixer.py
---------------
Core pipeline: background removal -> sharpen/enhance -> studio white canvas.
Imported by both app.py (Streamlit UI) and cli.py (batch/terminal use).
"""

import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

try:
    from rembg import remove as rembg_remove
except ImportError:
    rembg_remove = None

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def remove_background(image: Image.Image) -> Image.Image:
    """Return an RGBA image with the background removed."""
    if rembg_remove is None:
        raise RuntimeError("rembg not installed. Run: pip install rembg onnxruntime")
    result = rembg_remove(image)
    return result.convert("RGBA")


def sharpen_and_enhance(cutout: Image.Image) -> Image.Image:
    """Light sharpening + contrast/color boost so the product pops."""
    rgb = cutout.convert("RGB")
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    rgb = ImageEnhance.Color(rgb).enhance(1.05)
    r, g, b = rgb.split()
    return Image.merge("RGBA", (r, g, b, cutout.split()[-1]))


def get_content_bbox(cutout: Image.Image):
    """Bounding box of the non-transparent pixels, to crop tight to the product."""
    alpha = np.array(cutout.split()[-1])
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0 or len(ys) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


def place_on_white_canvas(
    cutout: Image.Image, canvas_size: int = 1600, padding_ratio: float = 0.10
) -> Image.Image:
    """Crop tight to the product, then center it on a square white canvas."""
    bbox = get_content_bbox(cutout)
    cropped = cutout.crop(bbox) if bbox else cutout

    usable = int(canvas_size * (1 - 2 * padding_ratio))
    scale = min(usable / cropped.width, usable / cropped.height)
    new_w, new_h = max(1, int(cropped.width * scale)), max(1, int(cropped.height * scale))
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
    offset = ((canvas_size - new_w) // 2, (canvas_size - new_h) // 2)
    canvas.paste(resized, offset, mask=resized.split()[-1])
    return canvas


def process_image(
    original: Image.Image, canvas_size: int = 1600, padding_ratio: float = 0.10
) -> Image.Image:
    """Full pipeline for one already-opened PIL image -> studio-finished PIL image."""
    original = original.convert("RGB")
    cutout = remove_background(original)
    cutout = sharpen_and_enhance(cutout)
    return place_on_white_canvas(cutout, canvas_size=canvas_size, padding_ratio=padding_ratio)
