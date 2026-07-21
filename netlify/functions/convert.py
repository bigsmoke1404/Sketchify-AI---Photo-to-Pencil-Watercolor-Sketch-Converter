"""
convert.py — Netlify Serverless Function
Handles image conversion (Pencil Sketch & Watercolor) using Pillow + NumPy.
Accepts JSON body with base64-encoded image, returns base64-encoded result.
"""

import json
import base64
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np


# ──────────────────────────────────────────────
#  Image Processing Functions (Pillow-based)
# ──────────────────────────────────────────────

def pencil_sketch_pil(img_pil, intensity=0.5, edge_strength=0.5):
    """
    Pencil sketch effect using the dodge-blend technique.
    - Convert to grayscale
    - Invert
    - Gaussian blur (radius controlled by intensity)
    - Divide original by inverted-blur (dodge blend)
    """
    gray = img_pil.convert('L')
    inverted = ImageOps.invert(gray)

    # Map intensity 0-1 → blur radius 5-25
    blur_radius = max(5, int(intensity * 25))
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    gray_array = np.array(gray, dtype=np.float64)
    blur_array = np.array(blurred, dtype=np.float64)

    # Dodge blend: sketch = gray / (1 - blur/255)
    denominator = 1.0 - (blur_array / 255.0)
    denominator = np.clip(denominator, 1e-6, None)  # avoid division by zero
    sketch_array = np.clip(gray_array / denominator, 0, 255).astype(np.uint8)

    # Apply edge strength by blending with original grayscale
    # Higher edge_strength → sharper (closer to pure sketch)
    blend = (1.0 - edge_strength) * gray_array + edge_strength * sketch_array
    blend = np.clip(blend, 0, 255).astype(np.uint8)

    return Image.fromarray(blend, mode='L').convert('RGB')


def watercolor_sketch_pil(img_pil, smoothness=0.5):
    """
    Watercolor effect using Pillow.
    - Multiple median filter passes (edge-preserving smoothing)
    - Saturation and contrast boost for a painterly look
    """
    img = img_pil.convert('RGB')

    # Number of smoothing iterations (1-6) based on smoothness slider
    n_iter = max(1, int(smoothness * 6))
    result = img.copy()
    for _ in range(n_iter):
        result = result.filter(ImageFilter.MedianFilter(size=5))

    # Boost saturation for the watercolor vibrancy
    result = ImageEnhance.Color(result).enhance(1.7)

    # Smooth edges slightly
    result = result.filter(ImageFilter.SMOOTH_MORE)

    # Slight contrast bump
    result = ImageEnhance.Contrast(result).enhance(1.15)

    return result


# ──────────────────────────────────────────────
#  Netlify Function Handler
# ──────────────────────────────────────────────

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
}


def handler(event, context):
    """Entry point for Netlify Function."""

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        # Decode body (may be base64-encoded by API Gateway)
        body = event.get('body', '') or ''
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')

        data = json.loads(body)

        # Extract image (data URL or raw base64)
        image_data = data.get('image', '')
        if not image_data:
            return _error('No image provided', 400)

        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]

        # Basic size guard (~10MB of base64)
        if len(image_data) > 13_500_000:
            return _error('Image too large. Maximum size is 10 MB.', 413)

        # Open image with Pillow
        img_bytes = base64.b64decode(image_data)
        img = Image.open(BytesIO(img_bytes))

        # Normalise colour mode
        if img.mode in ('RGBA', 'P', 'LA', 'CMYK'):
            img = img.convert('RGB')

        # Read slider params
        filter_type  = data.get('filter_type', 'pencil')
        intensity    = float(data.get('intensity', 0.5))
        edge_strength = float(data.get('edge_strength', 0.5))
        smoothness   = float(data.get('smoothness', 0.5))

        # Apply selected filter
        if filter_type == 'pencil':
            result_img = pencil_sketch_pil(img, intensity, edge_strength)
        elif filter_type == 'watercolor':
            result_img = watercolor_sketch_pil(img, smoothness)
        else:
            return _error('Invalid filter type', 400)

        # Encode result as JPEG base64
        buf = BytesIO()
        result_img.save(buf, format='JPEG', quality=92)
        result_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'success': True,
                'converted_image': 'data:image/jpeg;base64,' + result_b64
            })
        }

    except Exception as exc:
        return _error(str(exc), 500)


def _error(message, status=500):
    return {
        'statusCode': status,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': message})
    }
