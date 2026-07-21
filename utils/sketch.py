"""
sketch.py - Core image processing for Sketchify AI
Refactored for Streamlit: accepts PIL Images, returns PIL Images (no file I/O).
Uses OpenCV for high-quality artistic effects.
"""

import cv2
import numpy as np
from PIL import Image


# ──────────────────────────────────────────────
#  Conversion helpers
# ──────────────────────────────────────────────

def _pil_to_bgr(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL RGB Image → OpenCV BGR ndarray."""
    return cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)


def _gray_to_pil(gray: np.ndarray) -> Image.Image:
    """Convert OpenCV grayscale ndarray → RGB PIL Image."""
    return Image.fromarray(cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB))


def _bgr_to_pil(bgr: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR ndarray → RGB PIL Image."""
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


# ──────────────────────────────────────────────
#  Pencil Sketch
# ──────────────────────────────────────────────

def pencil_sketch(pil_img: Image.Image, intensity: float = 0.5, edge_strength: float = 0.5) -> Image.Image:
    """
    Convert a PIL Image to a grayscale pencil sketch.

    Uses cv2.pencilSketch (stylization module) for premium quality.
    Falls back to a manual dodge-blend if the module is unavailable.

    Args:
        pil_img:       Input image (PIL Image, any mode).
        intensity:     0.0-1.0  — sigma_s / blur amount (spatial range).
        edge_strength: 0.0-1.0  — sigma_r / edge sensitivity.

    Returns:
        Pencil sketch as RGB PIL Image.
    """
    img_bgr = _pil_to_bgr(pil_img)

    # Map 0-1 params to cv2.pencilSketch ranges
    sigma_s = int(intensity * 180) + 20        # 20 – 200
    sigma_r = float(edge_strength) * 0.9 + 0.1 # 0.1 – 1.0

    try:
        gray_sketch, _ = cv2.pencilSketch(
            img_bgr, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=0.05
        )
        return _gray_to_pil(gray_sketch)
    except cv2.error:
        # Fallback: manual dodge-blend
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur_r = max(3, sigma_s // 10)
        if blur_r % 2 == 0:
            blur_r += 1
        blurred = cv2.GaussianBlur(inverted, (blur_r, blur_r), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
        result = cv2.addWeighted(gray, 1.0 - edge_strength, sketch, edge_strength, 0)
        return _gray_to_pil(np.clip(result, 0, 255).astype(np.uint8))


# ──────────────────────────────────────────────
#  Watercolor Sketch
# ──────────────────────────────────────────────

def watercolor_sketch(pil_img: Image.Image, smoothness: float = 0.5) -> Image.Image:
    """
    Convert a PIL Image to a watercolor painting effect.

    Uses cv2.stylization with edgePreservingFilter for a rich paint-like look.
    Falls back to bilateral filter + adaptiveThreshold if unavailable.

    Args:
        pil_img:    Input image (PIL Image, any mode).
        smoothness: 0.0-1.0 — controls smoothing & stylisation intensity.

    Returns:
        Watercolor effect as RGB PIL Image.
    """
    img_bgr = _pil_to_bgr(pil_img)

    sigma_s = int(smoothness * 180) + 20        # 20 – 200
    sigma_r = float(smoothness) * 0.8 + 0.1     # 0.1 – 0.9

    try:
        smoothed = cv2.edgePreservingFilter(img_bgr, flags=1, sigma_s=sigma_s, sigma_r=sigma_r)
        stylized = cv2.stylization(smoothed, sigma_s=sigma_s, sigma_r=sigma_r)
        return _bgr_to_pil(stylized)
    except cv2.error:
        # Fallback: bilateral filter + edge mask
        n = max(1, int(smoothness * 5) + 1)
        result = img_bgr.copy()
        for _ in range(n):
            result = cv2.bilateralFilter(result, 9, 75, 75)
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return _bgr_to_pil(cv2.bitwise_and(result, edges_bgr))
