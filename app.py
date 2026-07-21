"""
app.py — Local Flask development server for Sketchify AI.
Serves the `public/` static frontend and exposes a /convert endpoint
that uses the same Pillow algorithms as the Netlify serverless function,
so local and production behaviour are identical.

Run:  python app.py
Open: http://127.0.0.1:5000
"""

from __future__ import annotations

import base64
import json
import os
from io import BytesIO

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image

from utils.sketch import pencil_sketch, watercolor_sketch

# ─── Flask App ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)   # we handle static ourselves

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

# ─── Static frontend routes ───────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.route("/about")
def about():
    return send_from_directory(PUBLIC_DIR, "about.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(PUBLIC_DIR, "static"), filename)


# ─── Conversion endpoint ───────────────────────────────────────────────────────

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
}


@app.route("/convert", methods=["POST", "OPTIONS"])
def convert():
    """
    Mirrors the Netlify serverless function API.
    Accepts JSON: { image: "<base64 data URL>", filter_type, intensity,
                    edge_strength, smoothness }
    Returns JSON: { success, converted_image: "<base64 data URL>" }
    """
    if request.method == "OPTIONS":
        return ("", 200, CORS_HEADERS)

    try:
        data = request.get_json(force=True)

        image_data: str = data.get("image", "")
        if not image_data:
            return jsonify({"error": "No image provided"}), 400

        # Strip data-URL prefix
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        if len(image_data) > 13_500_000:     # ~10 MB raw
            return jsonify({"error": "Image too large. Maximum 10 MB."}), 413

        # Decode + open
        img_bytes = base64.b64decode(image_data)
        pil_img   = Image.open(BytesIO(img_bytes))

        # Normalise colour mode
        if pil_img.mode in ("RGBA", "P", "LA", "CMYK"):
            pil_img = pil_img.convert("RGB")
        else:
            pil_img = pil_img.convert("RGB")

        # Parameters
        filter_type   = data.get("filter_type",   "pencil")
        intensity     = float(data.get("intensity",      0.5))
        edge_strength = float(data.get("edge_strength",  0.5))
        smoothness    = float(data.get("smoothness",     0.5))

        # Process
        if filter_type == "pencil":
            result = pencil_sketch(pil_img, intensity=intensity, edge_strength=edge_strength)
        elif filter_type == "watercolor":
            result = watercolor_sketch(pil_img, smoothness=smoothness)
        else:
            return jsonify({"error": "Invalid filter_type"}), 400

        # Encode result
        buf = BytesIO()
        result.save(buf, format="JPEG", quality=92)
        result_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return jsonify({
            "success":         True,
            "converted_image": "data:image/jpeg;base64," + result_b64,
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n  🎨  Sketchify AI — Local Dev Server")
    print("  ✅  Open http://127.0.0.1:5000\n")
    app.run(debug=True, use_reloader=False, threaded=True, port=5000)
