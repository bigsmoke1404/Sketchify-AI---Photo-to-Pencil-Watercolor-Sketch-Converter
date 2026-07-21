/**
 * main.js — Sketchify AI Frontend Logic
 * Handles: Dark Mode, Drag & Drop, Form Submission, Before/After Slider, Toasts, Keyboard Shortcuts
 */

document.addEventListener('DOMContentLoaded', () => {

    // ==============================================
    //  DARK MODE
    // ==============================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const themeIcon = themeToggleBtn?.querySelector('i');

    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const current = htmlElement.getAttribute('data-bs-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
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
    //  FILTER TOGGLE (Pencil / Watercolor settings)
    // ==============================================
    const filterType = document.getElementById('filterType');
    const pencilSettings = document.getElementById('pencilSettings');
    const watercolorSettings = document.getElementById('watercolorSettings');

    if (filterType) {
        filterType.addEventListener('change', (e) => {
            if (e.target.value === 'pencil') {
                pencilSettings.classList.remove('d-none');
                watercolorSettings.classList.add('d-none');
            } else {
                pencilSettings.classList.add('d-none');
                watercolorSettings.classList.remove('d-none');
            }
        });
    }

    // ==============================================
    //  SLIDER LABELS
    // ==============================================
    [
        { id: 'intensity', label: 'intensityVal' },
        { id: 'edgeStrength', label: 'edgeVal' },
        { id: 'smoothness', label: 'smoothVal' }
    ].forEach(({ id, label }) => {
        const el = document.getElementById(id);
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
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const uploadContent = document.getElementById('uploadContent');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const convertBtn = document.getElementById('convertBtn');

    let currentFile = null;

    if (uploadArea) {
        // Prevent browser defaults for drag events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
            uploadArea.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
        });

        ['dragenter', 'dragover'].forEach(evt =>
            uploadArea.addEventListener(evt, () => uploadArea.classList.add('dragover'))
        );

        ['dragleave', 'drop'].forEach(evt =>
            uploadArea.addEventListener(evt, () => uploadArea.classList.remove('dragover'))
        );

        uploadArea.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    }

    if (imageInput) {
        imageInput.addEventListener('change', function () {
            handleFiles(this.files);
        });
    }

    function handleFiles(files) {
        if (!files || files.length === 0) return;
        const file = files[0];

        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            showToast('Invalid file type. Only JPG and PNG are allowed.', 'danger');
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showToast('File is too large. Maximum allowed size is 10MB.', 'danger');
            return;
        }

        currentFile = file;

        // Show image preview
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
        removeImageBtn.addEventListener('click', e => {
            e.stopPropagation();
            resetUpload();
        });
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
    //  FORM SUBMISSION (AJAX)
    // ==============================================
    const convertForm = document.getElementById('convertForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultsArea = document.getElementById('resultsArea');
    const resetBtn = document.getElementById('resetBtn');
    const originalImage = document.getElementById('originalImage');
    const resultImage = document.getElementById('resultImage');
    const downloadBtn = document.getElementById('downloadBtn');

    if (convertForm) {
        convertForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!currentFile) {
                showToast('Please select an image first.', 'danger');
                return;
            }

            // Show loading
            convertBtn.setAttribute('disabled', 'true');
            showElement(loadingOverlay, 'flex');
            resultsArea.classList.add('d-none');

            // Build FormData — always set the file explicitly from currentFile
            const formData = new FormData();
            formData.append('image', currentFile, currentFile.name);
            formData.append('filter_type', document.getElementById('filterType').value);
            formData.append('intensity', document.getElementById('intensity').value);
            formData.append('edge_strength', document.getElementById('edgeStrength').value);
            formData.append('smoothness', document.getElementById('smoothness').value);

            try {
                const response = await fetch('/convert', { method: 'POST', body: formData });
                const data = await response.json();

                if (!response.ok) throw new Error(data.error || 'Conversion failed');

                // ---- Success ----
                // Wait for both images to load before showing results
                await Promise.all([
                    loadImg(originalImage, data.original_image),
                    loadImg(resultImage, data.converted_image)
                ]);

                // Set download link
                downloadBtn.href = data.converted_image;
                downloadBtn.setAttribute('download', 'sketchify_result.jpg');

                // Hide loading, show results
                hideElement(loadingOverlay);
                showElement(resultsArea);
                resetBtn.classList.remove('d-none');

                // Initialize the comparison slider now that images are loaded
                initSlider();

                // Scroll to results smoothly
                setTimeout(() => {
                    resultsArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 100);

                showToast('Image converted successfully! ✨', 'success');

            } catch (err) {
                hideElement(loadingOverlay);
                convertBtn.removeAttribute('disabled');
                showToast('Error: ' + err.message, 'danger');
            }
        });
    }

    // Helper: show a hidden element with optional display type
    function showElement(el, display = 'block') {
        if (!el) return;
        el.classList.remove('d-none');
        el.style.display = display;
    }

    function hideElement(el) {
        if (!el) return;
        el.classList.add('d-none');
        el.style.display = '';
    }

    // Helper: return a Promise that resolves when an image finishes loading
    function loadImg(imgEl, src) {
        return new Promise((resolve) => {
            imgEl.onload = resolve;
            imgEl.onerror = resolve; // resolve anyway so we don't hang forever
            imgEl.src = src;
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            resetUpload();
            hideElement(resultsArea);
            resetBtn.classList.add('d-none');
            const converterSection = document.getElementById('converter');
            if (converterSection) {
                converterSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    // ==============================================
    //  BEFORE / AFTER COMPARISON SLIDER
    // ==============================================
    function initSlider() {
        const container = document.getElementById('compareContainer');
        const handle = document.getElementById('sliderHandle');
        const wrapper = document.getElementById('originalWrapper');

        if (!container || !handle || !wrapper) return;

        const containerWidth = container.offsetWidth;

        // Make originalImage exactly the full container width so clipping works
        originalImage.style.width = containerWidth + 'px';

        // Reset to 50%
        let percent = 50;
        applySlider(percent);

        let isDragging = false;

        handle.addEventListener('mousedown', (e) => { isDragging = true; e.preventDefault(); });
        handle.addEventListener('touchstart', (e) => { isDragging = true; }, { passive: true });

        window.addEventListener('mouseup', () => { isDragging = false; });
        window.addEventListener('touchend', () => { isDragging = false; });

        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            percent = calcPercent(e.clientX, container);
            applySlider(percent);
        });

        window.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            percent = calcPercent(e.touches[0].clientX, container);
            applySlider(percent);
        }, { passive: true });

        // Re-apply on window resize
        window.addEventListener('resize', () => {
            const w = container.offsetWidth;
            originalImage.style.width = w + 'px';
            applySlider(percent);
        });

        function calcPercent(clientX, el) {
            const rect = el.getBoundingClientRect();
            let x = clientX - rect.left;
            x = Math.max(0, Math.min(x, rect.width));
            return (x / rect.width) * 100;
        }

        function applySlider(pct) {
            wrapper.style.width = pct + '%';
            handle.style.left = pct + '%';
            // Keep handle vertically centred (transform X only)
            handle.style.transform = 'translate(-50%, -50%)';
        }
    }

    // ==============================================
    //  KEYBOARD SHORTCUTS
    // ==============================================
    document.addEventListener('keydown', (e) => {
        // Esc — reset
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
    const toastEl = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastMessage');
    if (!toastEl || !toastBody) return;

    toastBody.textContent = message;

    // Reset classes, then apply type
    toastEl.className = `toast align-items-center text-white border-0 bg-${type}`;

    const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3500 });
    bsToast.show();
}
