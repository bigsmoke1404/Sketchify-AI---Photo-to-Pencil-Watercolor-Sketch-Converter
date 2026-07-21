/**
 * main.js — Sketchify AI Frontend Logic
 * Works on both Netlify (serverless) and local Flask development.
 */

// Detect environment: local Flask vs Netlify production
const IS_LOCAL = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const CONVERT_API = IS_LOCAL ? '/convert' : '/.netlify/functions/convert';

document.addEventListener('DOMContentLoaded', () => {

    // ==============================================
    //  DARK MODE
    // ==============================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const themeIcon = themeToggleBtn?.querySelector('i');

    applyTheme(localStorage.getItem('theme') || 'dark');

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            applyTheme(htmlElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
        });
    }

    function applyTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    }

    // ==============================================
    //  FILTER TOGGLE
    // ==============================================
    const filterType = document.getElementById('filterType');
    const pencilSettings = document.getElementById('pencilSettings');
    const watercolorSettings = document.getElementById('watercolorSettings');

    if (filterType) {
        filterType.addEventListener('change', (e) => {
            pencilSettings.classList.toggle('d-none', e.target.value !== 'pencil');
            watercolorSettings.classList.toggle('d-none', e.target.value === 'pencil');
        });
    }

    // ==============================================
    //  SLIDER LABELS
    // ==============================================
    [
        { id: 'intensity',   label: 'intensityVal' },
        { id: 'edgeStrength', label: 'edgeVal' },
        { id: 'smoothness',  label: 'smoothVal' }
    ].forEach(({ id, label }) => {
        const el  = document.getElementById(id);
        const lbl = document.getElementById(label);
        if (el && lbl) {
            el.addEventListener('input', () => {
                lbl.textContent = Math.round(parseFloat(el.value) * 100) + '%';
            });
        }
    });

    // ==============================================
    //  DRAG & DROP / FILE UPLOAD
    // ==============================================
    const uploadArea           = document.getElementById('uploadArea');
    const imageInput           = document.getElementById('imageInput');
    const uploadContent        = document.getElementById('uploadContent');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview         = document.getElementById('imagePreview');
    const removeImageBtn       = document.getElementById('removeImageBtn');
    const convertBtn           = document.getElementById('convertBtn');

    let currentFile = null;

    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt =>
            uploadArea.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); })
        );
        ['dragenter', 'dragover'].forEach(evt =>
            uploadArea.addEventListener(evt, () => uploadArea.classList.add('dragover'))
        );
        ['dragleave', 'drop'].forEach(evt =>
            uploadArea.addEventListener(evt, () => uploadArea.classList.remove('dragover'))
        );
        uploadArea.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    }

    if (imageInput) {
        imageInput.addEventListener('change', function () { handleFiles(this.files); });
    }

    function handleFiles(files) {
        if (!files || !files.length) return;
        const file = files[0];

        if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
            showToast('Invalid file type. Only JPG and PNG allowed.', 'danger');
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showToast('File too large. Max 10 MB allowed.', 'danger');
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        reader.onloadend = () => {
            imagePreview.src = reader.result;
            uploadContent.classList.add('d-none');
            imagePreviewContainer.classList.remove('d-none');
            convertBtn.removeAttribute('disabled');
        };
        reader.readAsDataURL(file);
    }

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', e => { e.stopPropagation(); resetUpload(); });
    }

    function resetUpload() {
        currentFile = null;
        if (imageInput) imageInput.value = '';
        imagePreview.src = '';
        uploadContent.classList.remove('d-none');
        imagePreviewContainer.classList.add('d-none');
        convertBtn.setAttribute('disabled', 'true');
    }

    // ==============================================
    //  FORM SUBMISSION
    // ==============================================
    const convertForm   = document.getElementById('convertForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultsArea   = document.getElementById('resultsArea');
    const resetBtn      = document.getElementById('resetBtn');
    const originalImage = document.getElementById('originalImage');
    const resultImage   = document.getElementById('resultImage');
    const downloadBtn   = document.getElementById('downloadBtn');

    if (convertForm) {
        convertForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!currentFile) { showToast('Please select an image first.', 'danger'); return; }

            // Show loader
            convertBtn.setAttribute('disabled', 'true');
            showEl(loadingOverlay);
            resultsArea.classList.add('d-none');

            try {
                let responseData;

                if (IS_LOCAL) {
                    // ── Local Flask: send as multipart FormData ──
                    const formData = new FormData();
                    formData.append('image', currentFile, currentFile.name);
                    formData.append('filter_type', filterType.value);
                    formData.append('intensity',   document.getElementById('intensity').value);
                    formData.append('edge_strength', document.getElementById('edgeStrength').value);
                    formData.append('smoothness',  document.getElementById('smoothness').value);

                    const res = await fetch(CONVERT_API, { method: 'POST', body: formData });
                    responseData = await res.json();
                    if (!res.ok) throw new Error(responseData.error || 'Conversion failed');

                    // Local: images are file paths, load them normally
                    await Promise.all([
                        loadImgSrc(originalImage, responseData.original_image),
                        loadImgSrc(resultImage,   responseData.converted_image)
                    ]);

                    // Download via file URL
                    downloadBtn.href = responseData.converted_image;
                    downloadBtn.setAttribute('download', 'sketchify_result.jpg');

                } else {
                    // ── Netlify: send as JSON with base64 image ──
                    const imageBase64 = await fileToBase64(currentFile);

                    const payload = {
                        image:        imageBase64,
                        filter_type:  filterType.value,
                        intensity:    parseFloat(document.getElementById('intensity').value),
                        edge_strength: parseFloat(document.getElementById('edgeStrength').value),
                        smoothness:   parseFloat(document.getElementById('smoothness').value)
                    };

                    const res = await fetch(CONVERT_API, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    responseData = await res.json();
                    if (!res.ok) throw new Error(responseData.error || 'Conversion failed');

                    // Netlify: images are base64 data URLs
                    originalImage.src = imagePreview.src; // already loaded in preview
                    resultImage.src   = responseData.converted_image;

                    // Create blob URL for proper download
                    const blob    = dataURLtoBlob(responseData.converted_image);
                    const blobUrl = URL.createObjectURL(blob);
                    downloadBtn.href = blobUrl;
                    downloadBtn.setAttribute('download', 'sketchify_result.jpg');
                }

                // Wait for result image to render
                await new Promise(r => setTimeout(r, 300));

                hideEl(loadingOverlay);
                showEl(resultsArea);
                resetBtn.classList.remove('d-none');
                initSlider();
                resultsArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                showToast('Image converted successfully! ✨', 'success');

            } catch (err) {
                hideEl(loadingOverlay);
                convertBtn.removeAttribute('disabled');
                showToast('Error: ' + err.message, 'danger');
            }
        });
    }

    // Helper — show element
    function showEl(el) { if (el) { el.classList.remove('d-none'); el.style.display = 'block'; } }
    function hideEl(el) { if (el) { el.classList.add('d-none'); el.style.display = ''; } }

    // Helper — load image src as Promise
    function loadImgSrc(imgEl, src) {
        return new Promise(resolve => {
            imgEl.onload = imgEl.onerror = resolve;
            imgEl.src = src;
        });
    }

    // Helper — File → base64 data URL
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    // Helper — base64 data URL → Blob (for download)
    function dataURLtoBlob(dataURL) {
        const [header, base64] = dataURL.split(',');
        const mime = header.match(/:(.*?);/)[1];
        const binary = atob(base64);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
        return new Blob([array], { type: mime });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            resetUpload();
            hideEl(resultsArea);
            resetBtn.classList.add('d-none');
            const sec = document.getElementById('converter');
            if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }

    // ==============================================
    //  BEFORE / AFTER COMPARISON SLIDER
    // ==============================================
    function initSlider() {
        const container = document.getElementById('compareContainer');
        const handle    = document.getElementById('sliderHandle');
        const wrapper   = document.getElementById('originalWrapper');
        if (!container || !handle || !wrapper) return;

        // Set inner image width to full container width so clipping looks correct
        originalImage.style.width = container.offsetWidth + 'px';

        let pct = 50;
        applySlider(pct);
        let dragging = false;

        handle.addEventListener('mousedown',  e => { dragging = true; e.preventDefault(); });
        handle.addEventListener('touchstart', () => { dragging = true; }, { passive: true });
        window.addEventListener('mouseup',    () => { dragging = false; });
        window.addEventListener('touchend',   () => { dragging = false; });

        window.addEventListener('mousemove', e => {
            if (!dragging) return;
            pct = getPercent(e.clientX, container);
            applySlider(pct);
        });
        window.addEventListener('touchmove', e => {
            if (!dragging) return;
            pct = getPercent(e.touches[0].clientX, container);
            applySlider(pct);
        }, { passive: true });

        window.addEventListener('resize', () => {
            originalImage.style.width = container.offsetWidth + 'px';
            applySlider(pct);
        });

        function getPercent(clientX, el) {
            const r = el.getBoundingClientRect();
            return Math.max(0, Math.min(100, ((clientX - r.left) / r.width) * 100));
        }
        function applySlider(p) {
            wrapper.style.width  = p + '%';
            handle.style.left    = p + '%';
            handle.style.transform = 'translate(-50%, -50%)';
        }
    }

    // ==============================================
    //  KEYBOARD SHORTCUTS
    // ==============================================
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            if (resetBtn && !resetBtn.classList.contains('d-none')) {
                resetBtn.click();
            } else if (removeImageBtn && imagePreviewContainer && !imagePreviewContainer.classList.contains('d-none')) {
                removeImageBtn.click();
            }
        }
    });
});

// ==============================================
//  TOAST (global — called from inline HTML too)
// ==============================================
function showToast(message, type = 'success') {
    const toastEl   = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastMessage');
    if (!toastEl || !toastBody) return;
    toastBody.textContent = message;
    toastEl.className = `toast align-items-center text-white border-0 bg-${type}`;
    bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3500 }).show();
}
