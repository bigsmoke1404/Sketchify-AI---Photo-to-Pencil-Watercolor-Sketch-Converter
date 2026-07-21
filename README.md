# Sketchify AI - Photo to Pencil & Watercolor Sketch Converter

![Sketchify AI](https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=800&auto=format&fit=crop)

Sketchify AI is a premium, professional-grade web application built using Flask and OpenCV. It allows users to upload an image and instantly convert it into stunning Pencil Sketches or Watercolor Art directly within the browser.

## Features
- **Two Unique Sketch Styles**: Choose between Pencil Sketch and Watercolor Sketch.
- **Advanced Adjustments**: Control intensity, edge thickness, and smoothness via intuitive sliders.
- **Modern UI/UX**: Designed with a sleek, responsive Glassmorphism theme using Bootstrap 5 and custom CSS.
- **Dark/Light Mode**: Toggle between themes seamlessly (saves preference in local storage).
- **Interactive Drag & Drop**: Easy file uploading with preview.
- **Before/After Comparison**: Compare original and converted images with a sliding handle.
- **Session History**: Keeps track of recent conversions during your active session.
- **AJAX Processing**: Fast processing without page reloads, accompanied by loading animations and toast notifications.

## Technology Stack
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (ES6)
- **Backend**: Python 3, Flask, Werkzeug
- **Image Processing**: OpenCV (cv2), NumPy, Pillow

## Folder Structure
```
SketchifyAI/
├── app.py                  # Main Flask application logic
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── static/
│   ├── css/
│   │   └── style.css       # Custom Glassmorphism styles
│   ├── js/
│   │   └── main.js         # Frontend interactions, AJAX, Drag&Drop
│   ├── uploads/            # Temporary storage for uploaded images
│   └── outputs/            # Storage for processed images
├── templates/
│   ├── layout.html         # Base template (Navbar, Footer)
│   ├── index.html          # Main converter and landing page
│   └── about.html          # Information about the technology used
└── utils/
    └── sketch.py           # OpenCV logic for applying filters
```

## Installation & Setup

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd SketchifyAI
   ```

2. **(Optional but recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Future Enhancements
- User authentication and cloud storage for saving portfolios.
- More OpenCV filters (e.g., Cartoonify, Oil Painting, Pointillism).
- Batch processing multiple images at once.
- Integration with AI models (e.g., Stable Diffusion) for advanced stylization.

## License
MIT License. Free to use and modify for educational or commercial purposes.
