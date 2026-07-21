/**
 * main.js — Sketchify AI Frontend
 *
 * API strategy:
 *   Local  (localhost/127.0.0.1) → POST /convert          (Flask, JSON+base64)
 *   Netlify (production)         → POST /.netlify/functions/convert  (same JSON+base64)
 *
 * Both endpoints share identical request/response shapes, so this JS
 * file works without any changes in either environment.
 */

'use strict';

// ── Environment detection ──────────────────────────────────────────────────
const IS_LOCAL = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const API_URL  = IS_LOCAL ? '/convert' : '/.netlify/functions/convert';

// ── DOM ready ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // ── Theme Toggle ──────────────────────────────────────────────────────
  const themeBtn  = document.getElementById('theme-toggle');
  const themeIcon = themeBtn?.querySelector('i');
  const html      = document.documentElement;

  const applyTheme = (t) => {
    html.setAttribute('data-bs-theme', t);
    localStorage.setItem('sketchify-theme', t);
    if (themeIcon) themeIcon.className = t === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  };

  applyTheme(localStorage.getItem('sketchify-theme') || 'dark');
  themeBtn?.addEventListener('click', () =>
    applyTheme(html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark')
  );

  // ── Filter panel toggle ────────────────────────────────────────────────
  const filterSelect       = document.getElementById('filterType');
  const pencilSettings     = document.getElementById('pencilSettings');
  const watercolorSettings = document.getElementById('watercolorSettings');

  filterSelect?.addEventListener('change', () => {
    const isPencil = filterSelect.value === 'pencil';
    pencilSettings    ?.classList.toggle('d-none', !isPencil);
    watercolorSettings?.classList.toggle('d-none',  isPencil);
  });

  // ── Range slider labels ────────────────────────────────────────────────
  [
    { slider: 'intensity',    label: 'intensityVal'  },
    { slider: 'edgeStrength', label: 'edgeVal'       },
    { slider: 'smoothness',   label: 'smoothVal'     },
  ].forEach(({ slider, label }) => {
    const el  = document.getElementById(slider);
    const lbl = document.getElementById(label);
    if (el && lbl) {
      const update = () => (lbl.textContent = Math.round(+el.value * 100) + '%');
      el.addEventListener('input', update);
      update();
    }
  });

  // ── Drag & Drop / File Upload ──────────────────────────────────────────
  const uploadArea              = document.getElementById('uploadArea');
  const imageInput              = document.getElementById('imageInput');
  const uploadContent           = document.getElementById('uploadContent');
  const imagePreviewContainer   = document.getElementById('imagePreviewContainer');
  const imagePreview            = document.getElementById('imagePreview');
  const removeImageBtn          = document.getElementById('removeImageBtn');
  const convertBtn              = document.getElementById('convertBtn');

  let currentFile = null;

  if (uploadArea) {
    ['dragenter','dragover','dragleave','drop'].forEach(evt =>
      uploadArea.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); })
    );
    ['dragenter','dragover'].forEach(evt =>
      uploadArea.addEventListener(evt, () => uploadArea.classList.add('dragover'))
    );
    ['dragleave','drop'].forEach(evt =>
      uploadArea.addEventListener(evt, () => uploadArea.classList.remove('dragover'))
    );
    uploadArea.addEventListener('drop',  e  => handleFiles(e.dataTransfer.files));
    uploadArea.addEventListener('click', () => imageInput?.click());
  }

  imageInput?.addEventListener('change', function () { handleFiles(this.files); });

  function handleFiles(files) {
    if (!files?.length) return;
    const file = files[0];
    if (!['image/jpeg','image/png','image/jpg'].includes(file.type)) {
      return showToast('❌ Invalid file type. Only JPG and PNG allowed.', 'danger');
    }
    if (file.size > 10 * 1024 * 1024) {
      return showToast('❌ File too large. Maximum 10 MB.', 'danger');
    }
    currentFile = file;
    const reader = new FileReader();
    reader.onloadend = () => {
      imagePreview.src = reader.result;
      uploadContent?.classList.add('d-none');
      imagePreviewContainer?.classList.remove('d-none');
      convertBtn?.removeAttribute('disabled');
    };
    reader.readAsDataURL(file);
  }

  removeImageBtn?.addEventListener('click', e => { e.stopPropagation(); resetUpload(); });

  function resetUpload() {
    currentFile = null;
    if (imageInput) imageInput.value = '';
    imagePreview.src = '';
    uploadContent?.classList.remove('d-none');
    imagePreviewContainer?.classList.add('d-none');
    convertBtn?.setAttribute('disabled', 'true');
  }

  // ── Form Submission ────────────────────────────────────────────────────
  const convertForm    = document.getElementById('convertForm');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const resultsArea    = document.getElementById('resultsArea');
  const resetBtn       = document.getElementById('resetBtn');
  const originalImage  = document.getElementById('originalImage');
  const resultImage    = document.getElementById('resultImage');
  const downloadBtn    = document.getElementById('downloadBtn');

  convertForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentFile) { showToast('Please select an image first.', 'danger'); return; }

    // Show loader
    convertBtn?.setAttribute('disabled', 'true');
    showEl(loadingOverlay, 'block');
    resultsArea?.classList.add('d-none');

    try {
      // Convert file to base64 data URL
      const imageBase64 = await fileToBase64(currentFile);

      const payload = {
        image:        imageBase64,
        filter_type:  filterSelect?.value || 'pencil',
        intensity:    parseFloat(document.getElementById('intensity')?.value    || 0.5),
        edge_strength: parseFloat(document.getElementById('edgeStrength')?.value || 0.5),
        smoothness:   parseFloat(document.getElementById('smoothness')?.value   || 0.5),
      };

      const res  = await fetch(API_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Conversion failed');

      // Display images
      originalImage.src = imagePreview.src;   // already loaded in preview
      resultImage.src   = data.converted_image;

      // Create blob URL for download
      const blob    = dataURLtoBlob(data.converted_image);
      const blobUrl = URL.createObjectURL(blob);
      if (downloadBtn) {
        downloadBtn.href = blobUrl;
        downloadBtn.setAttribute('download', 'sketchify_result.jpg');
      }

      // Show results
      hideEl(loadingOverlay);
      showEl(resultsArea, 'block');
      resetBtn?.classList.remove('d-none');

      await new Promise(r => setTimeout(r, 250));
      initSlider();
      resultsArea?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      showToast('✨ Image converted successfully!', 'success');

    } catch (err) {
      hideEl(loadingOverlay);
      convertBtn?.removeAttribute('disabled');
      showToast('❌ Error: ' + err.message, 'danger');
    }
  });

  // ── Helpers ────────────────────────────────────────────────────────────
  function showEl(el, display = 'block') {
    if (!el) return;
    el.classList.remove('d-none');
    el.style.display = display;
  }
  function hideEl(el) {
    if (!el) return;
    el.classList.add('d-none');
    el.style.display = '';
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const r = new FileReader();
      r.onloadend = () => resolve(r.result);
      r.onerror   = reject;
      r.readAsDataURL(file);
    });
  }

  function dataURLtoBlob(dataURL) {
    const [header, b64] = dataURL.split(',');
    const mime   = header.match(/:(.*?);/)[1];
    const binary = atob(b64);
    const arr    = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) arr[i] = binary.charCodeAt(i);
    return new Blob([arr], { type: mime });
  }

  // ── Reset button ───────────────────────────────────────────────────────
  resetBtn?.addEventListener('click', () => {
    resetUpload();
    hideEl(resultsArea);
    resetBtn.classList.add('d-none');
    document.getElementById('converter')?.scrollIntoView({ behavior:'smooth', block:'start' });
  });

  // ── Before/After Comparison Slider ────────────────────────────────────
  function initSlider() {
    const container = document.getElementById('compareContainer');
    const handle    = document.getElementById('sliderHandle');
    const wrapper   = document.getElementById('originalWrapper');
    if (!container || !handle || !wrapper) return;

    // Make inner image width match container so clip works correctly
    const inner = wrapper.querySelector('img');
    if (inner) inner.style.width = container.offsetWidth + 'px';

    let pct = 50;
    let dragging = false;

    apply(pct);

    handle.addEventListener('mousedown',  () => { dragging = true; });
    handle.addEventListener('touchstart', () => { dragging = true; }, { passive: true });
    window.addEventListener('mouseup',    () => { dragging = false; });
    window.addEventListener('touchend',   () => { dragging = false; });

    window.addEventListener('mousemove', e => {
      if (dragging) { pct = calc(e.clientX, container); apply(pct); }
    });
    window.addEventListener('touchmove', e => {
      if (dragging) { pct = calc(e.touches[0].clientX, container); apply(pct); }
    }, { passive: true });

    window.addEventListener('resize', () => {
      if (inner) inner.style.width = container.offsetWidth + 'px';
      apply(pct);
    });

    function calc(clientX, el) {
      const r = el.getBoundingClientRect();
      return Math.max(0, Math.min(100, ((clientX - r.left) / r.width) * 100));
    }
    function apply(p) {
      wrapper.style.width  = p + '%';
      handle.style.left    = p + '%';
    }
  }

  // ── Keyboard shortcuts ─────────────────────────────────────────────────
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (resetBtn && !resetBtn.classList.contains('d-none')) resetBtn.click();
      else if (!imagePreviewContainer?.classList.contains('d-none')) removeImageBtn?.click();
    }
  });

  // ── Navbar scroll shadow ───────────────────────────────────────────────
  const navbar = document.querySelector('.glass-navbar');
  window.addEventListener('scroll', () => {
    navbar?.classList.toggle('shadow-lg', window.scrollY > 20);
  });
});

// ── Toast (global) ─────────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const toastEl   = document.getElementById('liveToast');
  const toastBody = document.getElementById('toastMessage');
  if (!toastEl || !toastBody) return;
  toastBody.textContent = message;
  toastEl.className = `toast align-items-center text-white border-0 bg-${type}`;
  bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3500 }).show();
}
