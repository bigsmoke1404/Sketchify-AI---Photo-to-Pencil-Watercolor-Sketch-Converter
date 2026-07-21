"""
app.py — Sketchify AI (Streamlit Edition)
Deploy on Streamlit Community Cloud: https://streamlit.io/cloud
Run locally: streamlit run app.py
"""

import io
import streamlit as st
from PIL import Image
from utils.sketch import pencil_sketch, watercolor_sketch

# ─── Page Config (MUST be the very first Streamlit call) ─────────────────────
st.set_page_config(
    page_title="Sketchify AI — Photo to Sketch Converter",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com/bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter",
        "Report a bug": "https://github.com/bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter/issues",
        "About": "Sketchify AI — Transform your photos into stunning Pencil Sketches & Watercolor Art using OpenCV.",
    },
)

# ─── Session State ────────────────────────────────────────────────────────────
for key, default in [
    ("result_image", None),
    ("original_image", None),
    ("conversion_done", False),
    ("last_filter", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Premium Custom CSS ───────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* Global font */
*, *::before, *::after {
    font-family: 'Poppins', sans-serif !important;
}

/* App background */
.stApp {
    background: linear-gradient(135deg, #0F0F1A 0%, #1A1A2E 50%, #16213E 100%) !important;
}

/* Hide default Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Tighten page padding */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* ── Hero ──────────────────────────────────── */
.hero-wrap {
    background: linear-gradient(135deg, rgba(108,99,255,0.18) 0%, rgba(255,101,132,0.10) 100%);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    border-radius: 0 0 28px 28px;
    padding: 3.5rem 2rem 2.5rem;
    text-align: center;
    margin-bottom: 2.5rem;
}
.hero-logo   { font-size: 3.5rem; margin-bottom: 0; }
.hero-title  {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    background: linear-gradient(135deg, #A78BFA 0%, #6C63FF 45%, #FF6584 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15; margin-bottom: 0.6rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.55);
    max-width: 620px;
    margin: 0 auto 1.5rem;
}
.badge {
    display: inline-block;
    background: rgba(108,99,255,0.14);
    border: 1px solid rgba(108,99,255,0.35);
    color: #A5B4FC;
    padding: 0.28rem 0.85rem;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 0.2rem;
    letter-spacing: 0.02em;
}

/* ── Section labels ──────────────────────────── */
.step-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6C63FF;
    margin-bottom: 0.15rem;
}
.section-heading {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}

/* ── Buttons ─────────────────────────────────── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6C63FF, #FF6584) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.7rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    box-shadow: 0 4px 18px rgba(108,99,255,0.28) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(108,99,255,0.5) !important;
}
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.7rem 1.5rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 18px rgba(16,185,129,0.28) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(16,185,129,0.45) !important;
}

/* ── File uploader ───────────────────────────── */
div[data-testid="stFileUploadDropzone"] {
    background: rgba(108,99,255,0.06) !important;
    border: 2px dashed rgba(108,99,255,0.45) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    transition: all 0.3s !important;
}
div[data-testid="stFileUploadDropzone"]:hover {
    border-color: #6C63FF !important;
    background: rgba(108,99,255,0.12) !important;
}

/* ── Sliders ─────────────────────────────────── */
div[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.7) !important;
}

/* ── Select box ──────────────────────────────── */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* ── Tabs ────────────────────────────────────── */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: rgba(255,255,255,0.5) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #A78BFA !important;
}
div[data-baseweb="tab-highlight"] {
    background: linear-gradient(135deg, #6C63FF, #FF6584) !important;
    height: 3px !important;
    border-radius: 3px !important;
}

/* ── Metrics ─────────────────────────────────── */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    text-align: center !important;
}
div[data-testid="metric-container"] label {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.75rem !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #A78BFA !important;
    font-weight: 700 !important;
}

/* ── Info / helper boxes ─────────────────────── */
.info-box {
    background: rgba(108,99,255,0.07);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    color: rgba(255,255,255,0.65);
    font-size: 0.82rem;
    margin-top: 0.75rem;
}
.hint-text {
    text-align: center;
    color: rgba(255,255,255,0.3);
    font-size: 0.78rem;
    margin-top: 0.4rem;
}

/* ── Result section ──────────────────────────── */
.result-title {
    font-size: 1.9rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #A78BFA, #6C63FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.result-sub {
    text-align: center;
    color: rgba(255,255,255,0.45);
    font-size: 0.88rem;
    margin-bottom: 1.5rem;
}

/* ── About cards ─────────────────────────────── */
.about-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
}
.about-card h4 {
    color: #A78BFA;
    font-weight: 700;
    margin-bottom: 0.75rem;
    font-size: 1.05rem;
}
.about-card p, .about-card li {
    color: rgba(255,255,255,0.65);
    font-size: 0.88rem;
    line-height: 1.7;
}
.tech-grid { display:flex; flex-wrap:wrap; gap:0.6rem; margin-top:0.8rem; }
.tech-pill {
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.3);
    color: #A5B4FC;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── Footer ──────────────────────────────────── */
.custom-footer {
    text-align: center;
    padding: 2rem 1rem;
    color: rgba(255,255,255,0.25);
    font-size: 0.82rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 3rem;
}
.custom-footer a {
    color: rgba(167,139,250,0.7);
    text-decoration: none;
}
.custom-footer a:hover { color: #A78BFA; }

div[data-testid="stImage"] img {
    border-radius: 14px !important;
}

hr { border-color: rgba(255,255,255,0.07) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-wrap">
  <div class="hero-logo">🎨</div>
  <div class="hero-title">Sketchify AI</div>
  <div class="hero-title" style="font-size:clamp(1rem,2.8vw,1.5rem);margin-top:-0.4rem;opacity:0.85;">
    Photo to Pencil &amp; Watercolor Sketch Converter
  </div>
  <p class="hero-sub">
    Transform any photograph into stunning Pencil Sketches or Watercolor Art
    using AI-inspired OpenCV image processing — instantly, in your browser.
  </p>
  <div>
    <span class="badge">🐍 Python</span>
    <span class="badge">🎈 Streamlit</span>
    <span class="badge">👁️ OpenCV</span>
    <span class="badge">🖼️ Pillow</span>
    <span class="badge">📐 NumPy</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_conv, tab_about = st.tabs(["🖼️  Converter", "ℹ️  About"])

# ══════════════════════════════════════════════════════
#  CONVERTER TAB
# ══════════════════════════════════════════════════════
with tab_conv:

    # ── Upload + Settings columns ──────────────────────────────────────────
    col_up, col_set = st.columns([1.2, 1], gap="large")

    # ── Upload Column ──────────────────────────────────────────────────────
    with col_up:
        st.markdown(
            '<p class="step-label">Step 1</p><p class="section-heading">Upload Your Image</p>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Upload image",
            type=["jpg", "jpeg", "png"],
            help="Supported: JPG, JPEG, PNG · Max 10 MB",
            label_visibility="collapsed",
        )

        if uploaded_file:
            try:
                preview_pil = Image.open(uploaded_file).convert("RGB")
                st.image(preview_pil, caption="📸 Uploaded Image", use_container_width=True)
                w, h = preview_pil.size
                size_kb = uploaded_file.size // 1024
                st.markdown(
                    f'<div class="info-box">'
                    f"📂 <strong>{uploaded_file.name}</strong> &nbsp;·&nbsp; "
                    f"📐 {w} × {h} px &nbsp;·&nbsp; "
                    f"💾 {size_kb} KB"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.error(f"⚠️ Cannot read image: {exc}")
                uploaded_file = None
        else:
            st.markdown(
                '<div class="info-box" style="text-align:center;padding:2rem;">'
                "⬆️ Drag &amp; drop an image above, or click <strong>Browse files</strong>.<br>"
                '<span style="font-size:0.78rem;color:rgba(255,255,255,0.35)">JPG · PNG · up to 10 MB</span>'
                "</div>",
                unsafe_allow_html=True,
            )

    # ── Settings Column ────────────────────────────────────────────────────
    with col_set:
        st.markdown(
            '<p class="step-label">Step 2</p><p class="section-heading">Configure Settings</p>',
            unsafe_allow_html=True,
        )

        filter_choice = st.selectbox(
            "🎨 Filter Style",
            ["✏️  Pencil Sketch", "🎨  Watercolor Sketch"],
            help="Choose the artistic effect to apply",
        )

        st.markdown("---")

        is_pencil = "Pencil" in filter_choice

        if is_pencil:
            st.markdown("**✏️ Pencil Sketch Parameters**")
            intensity_pct = st.slider(
                "Sketch Strength",
                min_value=10, max_value=100, value=50, step=5,
                format="%d%%",
                help="Higher = softer, more diffuse pencil strokes (sigma_s)",
            )
            edge_pct = st.slider(
                "Edge Thickness",
                min_value=10, max_value=100, value=50, step=5,
                format="%d%%",
                help="Higher = sharper, bolder line edges (sigma_r)",
            )
            intensity    = intensity_pct / 100.0
            edge_strength = edge_pct / 100.0
            smoothness   = 0.5
        else:
            st.markdown("**🎨 Watercolor Parameters**")
            smooth_pct = st.slider(
                "Smoothness / Wash Intensity",
                min_value=10, max_value=100, value=50, step=5,
                format="%d%%",
                help="Higher = more smoothing passes, more painterly look",
            )
            smoothness   = smooth_pct / 100.0
            intensity    = 0.5
            edge_strength = 0.5

        st.markdown("---")
        st.markdown('<p class="step-label">Step 3</p>', unsafe_allow_html=True)

        convert_clicked = st.button(
            "⚡  Convert Image",
            disabled=(uploaded_file is None),
            use_container_width=True,
        )

        if not uploaded_file:
            st.markdown(
                '<p class="hint-text">← Upload an image first to enable conversion</p>',
                unsafe_allow_html=True,
            )

    # ── Conversion Logic ───────────────────────────────────────────────────
    if convert_clicked and uploaded_file:
        try:
            original_pil = Image.open(uploaded_file).convert("RGB")
            filter_key   = "pencil" if is_pencil else "watercolor"

            with st.spinner("⚡ Applying filter… this may take a few seconds"):
                if filter_key == "pencil":
                    result_pil = pencil_sketch(original_pil, intensity=intensity, edge_strength=edge_strength)
                else:
                    result_pil = watercolor_sketch(original_pil, smoothness=smoothness)

            st.session_state.result_image    = result_pil
            st.session_state.original_image  = original_pil
            st.session_state.conversion_done = True
            st.session_state.last_filter     = filter_key
            st.success("✅ Conversion complete!")

        except Exception as exc:
            st.error(f"❌ Conversion failed: {exc}")
            st.session_state.conversion_done = False

    # ── Results ────────────────────────────────────────────────────────────
    if st.session_state.conversion_done and st.session_state.result_image is not None:
        st.markdown("---")
        st.markdown(
            '<p class="result-title">✨ Conversion Result</p>'
            '<p class="result-sub">Drag the slider to compare Original vs Converted</p>',
            unsafe_allow_html=True,
        )

        # Before/After comparison slider
        try:
            from streamlit_image_comparison import image_comparison
            image_comparison(
                img1=st.session_state.original_image,
                img2=st.session_state.result_image,
                label1="📸 Original",
                label2="🎨 Converted",
                width=700,
                starting_position=50,
                show_labels=True,
                make_responsive=True,
                in_memory=True,
            )
        except ImportError:
            # Graceful fallback: side-by-side columns
            c1, c2 = st.columns(2)
            with c1:
                st.image(st.session_state.original_image, caption="📸 Original", use_container_width=True)
            with c2:
                st.image(st.session_state.result_image, caption="🎨 Converted", use_container_width=True)

        # Download button
        buf = io.BytesIO()
        st.session_state.result_image.save(buf, format="JPEG", quality=95)
        buf.seek(0)

        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, _ = st.columns([1, 1])
        with dl_col:
            st.download_button(
                label="⬇️  Download Result",
                data=buf,
                file_name="sketchify_result.jpg",
                mime="image/jpeg",
                use_container_width=True,
            )

        # Image metrics
        st.markdown("---")
        w, h = st.session_state.result_image.size
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Width",  f"{w} px")
        m2.metric("Height", f"{h} px")
        m3.metric("Filter", st.session_state.last_filter.capitalize() if st.session_state.last_filter else "—")
        m4.metric("Quality", "95%")

        # Reset button
        st.markdown("<br>", unsafe_allow_html=True)
        _, reset_col, _ = st.columns([1.5, 1, 1.5])
        with reset_col:
            if st.button("🔄  Reset", use_container_width=True):
                st.session_state.result_image    = None
                st.session_state.original_image  = None
                st.session_state.conversion_done = False
                st.session_state.last_filter     = None
                st.rerun()

# ══════════════════════════════════════════════════════
#  ABOUT TAB
# ══════════════════════════════════════════════════════
with tab_about:
    st.markdown("<br>", unsafe_allow_html=True)
    ac1, ac2 = st.columns(2, gap="large")

    with ac1:
        st.markdown(
            """
<div class="about-card">
<h4>🔬 What is Image Processing?</h4>
<p>Image processing involves applying mathematical transformations to pixel data to
produce an enhanced or artistically modified output. Sketchify AI uses OpenCV's
stylization filters to simulate the look of hand-drawn artwork.</p>
</div>

<div class="about-card">
<h4>✏️ How Pencil Sketch Works</h4>
<p>OpenCV's <code>cv2.pencilSketch()</code> uses a sigma-based spatial/range filter:</p>
<ol>
  <li>Convert to grayscale</li>
  <li>Apply bilateral-like spatial smoothing (sigma_s)</li>
  <li>Detect edges with a range threshold (sigma_r)</li>
  <li>Blend to produce the classic pencil-on-paper look</li>
</ol>
</div>
""",
            unsafe_allow_html=True,
        )

    with ac2:
        st.markdown(
            """
<div class="about-card">
<h4>🎨 How Watercolor Works</h4>
<p>The watercolor effect chains two OpenCV photo-art filters:</p>
<ol>
  <li><code>edgePreservingFilter</code> — smooths colour regions while preserving edges</li>
  <li><code>stylization</code> — adds the characteristic ink-outline + wash look</li>
</ol>
<p>Both steps are parameterised by <em>sigma_s</em> (spatial) and <em>sigma_r</em> (range).</p>
</div>

<div class="about-card">
<h4>🛠️ Tech Stack</h4>
<div class="tech-grid">
  <span class="tech-pill">🐍 Python 3.10+</span>
  <span class="tech-pill">🎈 Streamlit</span>
  <span class="tech-pill">👁️ OpenCV</span>
  <span class="tech-pill">🖼️ Pillow</span>
  <span class="tech-pill">📐 NumPy</span>
  <span class="tech-pill">☁️ Streamlit Cloud</span>
</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="about-card" style="margin-top:1rem;">
<h4>⭐ Benefits of Digital Sketching</h4>
<ul>
  <li><strong>Non-destructive</strong> — original photos remain perfectly intact</li>
  <li><strong>Instant</strong> — create beautiful art in seconds</li>
  <li><strong>Flexible</strong> — tune intensity/smoothness sliders for unique results</li>
  <li><strong>Accessible</strong> — no artistic skills required</li>
  <li><strong>Free</strong> — 100% open-source, runs on Streamlit Community Cloud</li>
</ul>
</div>
""",
        unsafe_allow_html=True,
    )

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="custom-footer">
  <p>🎨 <strong>Sketchify AI</strong> — Built with Streamlit · OpenCV · Pillow</p>
  <p>
    <a href="https://github.com/bigsmoke1404/Sketchify-AI---Photo-to-Pencil-Watercolor-Sketch-Converter"
       target="_blank">⭐ Star on GitHub</a>
    &nbsp;·&nbsp;
    <a href="https://streamlit.io/cloud" target="_blank">Deploy on Streamlit Cloud</a>
  </p>
</div>
""",
    unsafe_allow_html=True,
)
