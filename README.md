# 🎨 Sketchify AI — Photo to Pencil & Watercolor Sketch Converter

[![Netlify Status](https://api.netlify.com/api/v1/badges/placeholder/deploy-status)](https://app.netlify.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Pillow](https://img.shields.io/badge/Pillow-10.x-green)](https://python-pillow.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> Transform any photograph into stunning **Pencil Sketches** or **Watercolor Art**
> using AI-inspired image processing — deployed as a static site on **Netlify** with
> a **Python serverless function** for processing.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ✏️ **Pencil Sketch** | Grayscale dodge-blend effect |
| 🎨 **Watercolor** | Edge-preserving median filter + saturation boost |
| 🎚️ **Adjustable sliders** | Intensity, edge thickness, smoothness |
| 🔄 **Before/After slider** | Interactive comparison of original vs result |
| ⬇️ **Download** | Export result as JPEG (quality 92%) |
| 🌙 **Dark/Light mode** | Persisted theme toggle |
| 📱 **Responsive** | Desktop & mobile friendly |

---

## 🏗️ Architecture

```
Browser (HTML/CSS/JS)
       │
       │ POST /convert  (JSON + base64 image)
       │
       ▼
Netlify Function  ←  netlify/functions/convert.py
   (Python 3.x)       Pillow + NumPy only (~20MB, fits 50MB limit)
       │
       │ JSON response (base64 result image)
       ▼
Browser (renders comparison slider + download)
```

**Local development** replaces the Netlify function with a Flask server (`app.py`)
that uses the **identical algorithm and API**, so local ↔ production is 100% consistent.

---

## 📦 Local Installation

### Prerequisites
- Python **3.10+**
- pip

### Windows

```powershell
# 1. Clone the repo
git clone https://github.com/bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter.git
cd Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter

# 2. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run locally
python app.py
```

### macOS / Linux

```bash
git clone https://github.com/bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter.git
cd Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## ☁️ Deploy on Netlify

### Option A — One-click via Netlify UI

1. Push this repo to GitHub.
2. Go to **[app.netlify.com](https://app.netlify.com)** → **"Add new site"** → **"Import an existing project"**.
3. Connect your GitHub repo.
4. Netlify auto-detects `netlify.toml`:
   - **Publish directory**: `public`
   - **Build command**: *(none)*
   - **Functions directory**: `netlify/functions`
5. Click **"Deploy site"**. Done in ~60 seconds. ✅

### Option B — Netlify CLI

```bash
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

### Environment Variables

No environment variables are required. The app is fully self-contained.

---

## 📁 Project Structure

```
sketchify/
├── public/                       # ← Static frontend (served by Netlify CDN)
│   ├── index.html                #   Main converter page
│   ├── about.html                #   About page
│   └── static/
│       ├── css/style.css         #   Premium dark glassmorphism theme
│       └── js/main.js            #   All frontend interactions
│
├── netlify/
│   └── functions/
│       ├── convert.py            # ← Python serverless function (Pillow)
│       └── requirements.txt      #   Function deps: Pillow + numpy only
│
├── utils/
│   └── sketch.py                 # Shared Pillow algorithms (used by app.py)
│
├── app.py                        # ← Local Flask dev server
├── requirements.txt              #   Local deps: Flask + Pillow + numpy
├── netlify.toml                  #   Netlify configuration
└── README.md
```

---

## 🎮 Usage

1. **Upload** a JPG or PNG image (max 10 MB) via drag & drop or click
2. **Select** a filter: ✏️ Pencil Sketch or 🎨 Watercolor
3. **Adjust** the sliders to fine-tune the effect
4. Click **⚡ Convert Image**
5. **Compare** original vs converted with the drag slider
6. Click **⬇️ Download Result** to save your artwork

---

## 🔬 How the Algorithms Work

### ✏️ Pencil Sketch (dodge-blend)
```
gray     = image.convert('L')
inverted = 255 - gray
blurred  = GaussianBlur(inverted, radius=intensity*25)
sketch   = gray / (1 - blurred/255)   # dodge blend
result   = lerp(gray, sketch, edge_strength)
```

### 🎨 Watercolor (iterative median filter)
```
for n in range(int(smoothness * 6)):
    image = MedianFilter(image, size=5)
image = enhance_color(image, 1.7)
image = smooth_more(image)
image = enhance_contrast(image, 1.15)
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Made with ❤️ using Python · Pillow · Netlify · Bootstrap 5</p>
