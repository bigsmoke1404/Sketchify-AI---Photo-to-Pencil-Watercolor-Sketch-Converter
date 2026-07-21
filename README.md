# 🎨 Sketchify AI — Photo to Pencil & Watercolor Sketch Converter

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green?logo=opencv)](https://opencv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> Transform any photograph into stunning **Pencil Sketches** or **Watercolor Art** using AI-inspired OpenCV image processing — deployed on Streamlit Community Cloud.

![Sketchify AI Demo](https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=800)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ✏️ **Pencil Sketch** | Grayscale dodge-blend effect via `cv2.pencilSketch` |
| 🎨 **Watercolor** | Smooth painterly effect via `cv2.stylization` |
| 🎚️ **Adjustable sliders** | Fine-tune strength, edge thickness, smoothness |
| 🔄 **Before/After slider** | Interactive `streamlit-image-comparison` widget |
| ⬇️ **Download** | Export result as high-quality JPEG (95%) |
| 📱 **Responsive** | Works on desktop & mobile |

---

## 🚀 Live Demo

Deploy on **Streamlit Community Cloud** — see deployment section below.

---

## 🛠️ Tech Stack

- **Frontend / App**: [Streamlit](https://streamlit.io)
- **Image Processing**: [OpenCV](https://opencv.org), [Pillow](https://python-pillow.org), [NumPy](https://numpy.org)
- **Comparison Slider**: [streamlit-image-comparison](https://github.com/fcakyon/streamlit-image-comparison)

---

## 📦 Local Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter.git
cd Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter

# 2. Create and activate virtual environment (recommended)
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501** automatically.

---

## ☁️ Deploy on Streamlit Community Cloud

1. **Fork / push** this repository to your GitHub account.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **"New app"** and fill in:
   - **Repository**: `bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **"Deploy!"** — Streamlit Cloud installs `requirements.txt` and launches the app.

> 💡 No additional configuration needed — `.streamlit/config.toml` is already included.

---

## 📁 Project Structure

```
sketchify/
├── app.py                    # ← Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Theme & server configuration
├── utils/
│   ├── __init__.py
│   └── sketch.py             # Image processing (OpenCV)
├── static/                   # Legacy static assets (Flask)
│   ├── css/style.css
│   └── js/main.js
├── templates/                # Legacy Jinja2 templates (Flask)
├── netlify/                  # Netlify serverless function (alternative)
├── .gitignore
└── README.md
```

---

## 🎮 Usage

1. **Upload** a JPG or PNG image (max 10 MB)
2. **Select** a filter: ✏️ Pencil Sketch or 🎨 Watercolor Sketch
3. **Adjust** sliders to fine-tune the effect
4. Click **⚡ Convert Image**
5. **Compare** original vs converted using the drag slider
6. Click **⬇️ Download Result** to save your artwork

---

## 📸 How the Algorithms Work

### ✏️ Pencil Sketch
Uses `cv2.pencilSketch()` with two parameters:
- **sigma_s** (spatial): Controls blur radius — higher = softer strokes
- **sigma_r** (range): Controls edge sensitivity — higher = bolder lines

### 🎨 Watercolor
Chains two OpenCV photo-art filters:
1. `cv2.edgePreservingFilter()` — smooths colour regions while preserving edges
2. `cv2.stylization()` — applies the characteristic ink-outline + colour wash

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

<p align="center">Made with ❤️ using Streamlit & OpenCV</p>
