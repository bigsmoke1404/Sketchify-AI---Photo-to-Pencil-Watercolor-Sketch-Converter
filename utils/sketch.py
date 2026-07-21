"""
utils/sketch.py — Shared Pillow-based image processing (Pencil Sketch & Watercolor).
Used by the local Flask dev server (app.py). Mirrors the algorithm in netlify/functions/convert.py
so that local and production results are identical.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def pencil_sketch(pil_img: Image.Image, intensity: float = 0.5, edge_strength: float = 0.5) -> Image.Image:
    """
    Grayscale pencil-sketch via the dodge-blend technique.

    Args:
        pil_img:       Input PIL Image (any mode).
        intensity:     0-1 → Gaussian blur radius (higher = softer strokes).
        edge_strength: 0-1 → How strongly sketch lines appear vs. flat grey.
    Returns:
        RGB PIL Image.
    """
    gray = pil_img.convert("L")
    inverted = ImageOps.invert(gray)

    blur_radius = max(5, int(intensity * 25))
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    gray_arr  = np.array(gray,    dtype=np.float64)
    blur_arr  = np.array(blurred, dtype=np.float64)

    denom   = np.clip(1.0 - blur_arr / 255.0, 1e-6, None)
    sketch  = np.clip(gray_arr / denom, 0, 255)

    blended = (1.0 - edge_strength) * gray_arr + edge_strength * sketch
    result  = np.clip(blended, 0, 255).astype(np.uint8)

    return Image.fromarray(result, mode="L").convert("RGB")


def watercolor_sketch(pil_img: Image.Image, smoothness: float = 0.5) -> Image.Image:
    """
    Watercolor effect via iterative median filtering + saturation boost.

    Args:
        pil_img:    Input PIL Image (any mode).
        smoothness: 0-1 → Number of median-filter passes.
    Returns:
        RGB PIL Image.
    """
    img    = pil_img.convert("RGB")
    n_iter = max(1, int(smoothness * 6))

    result = img.copy()
    for _ in range(n_iter):
        result = result.filter(ImageFilter.MedianFilter(size=5))

    result = ImageEnhance.Color(result).enhance(1.7)
    result = result.filter(ImageFilter.SMOOTH_MORE)
    result = ImageEnhance.Contrast(result).enhance(1.15)
    return result
