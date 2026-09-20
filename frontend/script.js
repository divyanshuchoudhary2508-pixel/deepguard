document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();

    // Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const samplesGrid = document.getElementById('samples-grid');
    const systemStatusDot = document.querySelector('#system-status .status-dot');
    const statusText = document.getElementById('status-text');

    const heroSection = document.getElementById('hero-section');
    const inputSection = document.getElementById('input-section');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');

    const progressBar = document.getElementById('progress-bar');
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');

    // Result elements
    const resultBadge = document.getElementById('result-badge');
    const resultLabel = document.getElementById('result-label');
    const badgeIcon = document.getElementById('badge-icon');
    const scoreValue = document.getElementById('score-value');
    const scoreCircle = document.getElementById('score-circle');

    const imgOriginal = document.getElementById('img-original');
    const imgHeatmapOverlay = document.getElementById('img-heatmap-overlay');
    const imgMeshOverlay = document.getElementById('img-mesh-overlay');
    const imgSplitOrig = document.getElementById('img-split-orig');
    const imgSplitHeat = document.getElementById('img-split-heat');
    const imgSplitMesh = document.getElementById('img-split-mesh');

    const opacitySlider = document.getElementById('opacity-slider');
    const opacityVal = document.getElementById('opacity-val');

    const modeOverlayBtn = document.getElementById('mode-overlay-btn');
    const modeMeshBtn = document.getElementById('mode-mesh-btn');
    const modeSplitBtn = document.getElementById('mode-split-btn');
    const viewerOverlay = document.getElementById('viewer-overlay');
    const viewerSplit = document.getElementById('viewer-split');

    // EXIF elements
    const exifCamera = document.getElementById('exif-camera');
    const exifSoftware = document.getElementById('exif-software');
    const exifC2pa = document.getElementById('exif-c2pa');
    const exifAiSig = document.getElementById('exif-ai-sig');
    const exifExplanation = document.getElementById('exif-explanation');
    const exifRiskBadge = document.getElementById('exif-risk-badge');

    // Landmark elements
    const lmCount = document.getElementById('lm-count');
    const lmEyeSym = document.getElementById('lm-eye-sym');
    const lmJawWarp = document.getElementById('lm-jaw-warp');
    const lmStatus = document.getElementById('lm-status');
    const landmarkBadge = document.getElementById('landmark-badge');

    const resetBtn = document.getElementById('reset-btn');
    const viewReportBtn = document.getElementById('view-report-btn');

    // Report modal elements
    const reportModal = document.getElementById('report-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const printReportBtn = document.getElementById('print-report-btn');

    const repId = document.getElementById('rep-id');
    const repTime = document.getElementById('rep-time');
    const repFilename = document.getElementById('rep-filename');
    const repModel = document.getElementById('rep-model');
    const repResultBox = document.getElementById('rep-result-box');
    const repLabel = document.getElementById('rep-label');
    const repConf = document.getElementById('rep-conf');
    const repImgOrig = document.getElementById('rep-img-orig');
    const repImgHeat = document.getElementById('rep-img-heat');
    const repDisclaimerText = document.getElementById('rep-disclaimer-text');

    let currentReportData = null;
    let currentPdfUrl = null;

    // Check System Health
    async function checkHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            if (data.status === 'ok') {
                systemStatusDot.classList.add('online');
                statusText.textContent = data.model_loaded ? 'Model Ready (Xception)' : 'Server Ready';
            }
        } catch (err) {
            statusText.textContent = 'Server Offline';
            systemStatusDot.style.backgroundColor = '#ef4444';
        }
    }

    // Load Built-in Samples
    async function loadSamples() {
        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            if (data.samples && data.samples.length > 0) {
                samplesGrid.innerHTML = '';
                data.samples.forEach(sample => {
                    const card = document.createElement('div');
                    card.className = 'sample-card';
                    const isFake = sample.hint_label.includes('DEEPFAKE');
                    card.innerHTML = `
                        <img src="${sample.url}" class="sample-img" alt="${sample.name}">
                        <div class="sample-name">${sample.name}</div>
                        <span class="sample-badge ${isFake ? 'fake' : 'real'}">${sample.hint_label}</span>
                    `;
                    card.addEventListener('click', () => analyzeSample(sample.name));
                    samplesGrid.appendChild(card);
                });
            }
        } catch (err) {
            console.warn('Could not load samples:', err);
        }
    }

    // Dropzone Event Listeners
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            analyzeFile(e.target.files[0]);
        }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            analyzeFile(files[0]);
        }
    });

    // Analyze Uploaded File
    async function analyzeFile(file) {
        const formData = new FormData();
        formData.append('image', file);
        await runAnalysisPipeline(formData);
    }

    // Analyze Sample File
    async function analyzeSample(sampleName) {
        const formData = new FormData();
        formData.append('sample_name', sampleName);
        await runAnalysisPipeline(formData);
    }

    // Pipeline Execution
    async function runAnalysisPipeline(formData) {
        // Show Loading state
        inputSection.classList.add('hidden');
        heroSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        resultSection.classList.add('hidden');

        // Reset progress bar & steps
        progressBar.style.width = '20%';
        step1.className = 'step active';
        step2.className = 'step';
        step3.className = 'step';

        setTimeout(() => {
            progressBar.style.width = '60%';
            step1.innerHTML = '<i data-lucide="check-circle-2"></i> Tensor Preprocessed (224x224)';
            step2.className = 'step active';
            step2.innerHTML = '<i data-lucide="loader-2"></i> Multi-Signal Analysis';
            lucide.createIcons();
        }, 500);

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();

            if (!res.ok || data.error) {
                alert(`Analysis Error: ${data.error || 'Server processing error'}`);
                resetUI();
                return;
            }

            progressBar.style.width = '100%';
            step2.innerHTML = '<i data-lucide="check-circle-2"></i> Multi-Signal Analysis Complete';
            step3.className = 'step active';
            step3.innerHTML = '<i data-lucide="check-circle-2"></i> Grad-CAM++ & PDF Report Ready';
            lucide.createIcons();

            setTimeout(() => {
                displayResults(data);
            }, 600);

        } catch (err) {
            alert(`Network or Server error: ${err.message}`);
            resetUI();
        }
    }

    // Display Results
    function displayResults(data) {
        currentReportData = data.report;
        currentPdfUrl = data.pdf_url;
        currentFilename = data.filename;
        currentLabel = data.label;

        if (fbToast) fbToast.classList.add('hidden');

        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');

        const isFake = data.label.includes('DEEPFAKE');


        // Badge styling
        resultLabel.textContent = data.label;
        if (isFake) {
            resultBadge.className = 'result-badge fake';
            badgeIcon.innerHTML = '<i data-lucide="shield-alert"></i>';
        } else {
            resultBadge.className = 'result-badge real';
            badgeIcon.innerHTML = '<i data-lucide="shield-check"></i>';
        }

        // Score
        scoreValue.textContent = `${data.confidence}%`;

        // Images
        imgOriginal.src = data.original_url;
        imgHeatmapOverlay.src = data.heatmap_url;
        imgMeshOverlay.src = data.landmark_url || data.original_url;

        imgSplitOrig.src = data.original_url;
        imgSplitHeat.src = data.heatmap_url;
        imgSplitMesh.src = data.landmark_url || data.original_url;

        // Reset Opacity
        opacitySlider.value = 70;
        opacityVal.textContent = '70%';
        imgHeatmapOverlay.style.opacity = '0.7';
        imgMeshOverlay.style.opacity = '0.7';

        // EXIF Metadata Population
        if (data.metadata) {
            const meta = data.metadata;
            exifCamera.textContent = `${meta.camera_make} ${meta.camera_model}`.replace('Unknown / None Unknown / None', 'Unknown / None');
            exifSoftware.textContent = meta.software || 'None detected';
            exifC2pa.textContent = meta.c2pa_credentials ? 'Signed (Digital Credentials Found)' : 'Not Signed';
            exifAiSig.textContent = meta.ai_signatures_found.length > 0 ? meta.ai_signatures_found.join(', ') : 'None';
            exifExplanation.textContent = meta.risk_explanation;

            exifRiskBadge.textContent = meta.metadata_risk_level;
            if (meta.metadata_risk_level === 'AI_GENERATED_SOFTWARE') {
                exifRiskBadge.className = 'badge-risk';
            } else if (meta.metadata_risk_level === 'AUTHENTIC_HARDWARE') {
                exifRiskBadge.className = 'badge-risk ok';
            } else {
                exifRiskBadge.className = 'badge-risk warn';
            }
        }

        // Facial Landmark Geometry Population
        if (data.landmarks) {
            const lm = data.landmarks;
            lmCount.textContent = `${lm.landmarks_count} Nodes Detected`;
            lmEyeSym.textContent = `${lm.eye_symmetry} (${lm.eye_symmetry > 0.85 ? 'Symmetrical' : 'Asymmetrical Delta'})`;
            lmJawWarp.textContent = `${lm.jawline_warp_index} (${lm.jawline_warp_index < 0.1 ? 'Smooth Contour' : 'Seam Discontinuity'})`;
            lmStatus.textContent = lm.status_message;

            if (lm.face_detected && lm.eye_symmetry > 0.85 && lm.jawline_warp_index < 0.1) {
                landmarkBadge.textContent = 'FACE MESH OK';
                landmarkBadge.className = 'badge-risk ok';
            } else if (lm.face_detected) {
                landmarkBadge.textContent = 'GEOMETRY ANOMALY';
                landmarkBadge.className = 'badge-risk';
            } else {
                landmarkBadge.textContent = 'NO FACE MESH';
                landmarkBadge.className = 'badge-risk warn';
            }
        }

        // Default view: Grad-CAM Overlay
        showGradCamView();

        // Re-init icons
        lucide.createIcons();
    }

    let currentFilename = null;
    let currentLabel = null;

    // Feedback DOM elements
    const fbAgreeBtn = document.getElementById('fb-agree-btn');
    const fbDisagreeBtn = document.getElementById('fb-disagree-btn');
    const fbToast = document.getElementById('fb-toast');
    const fbToastMsg = document.getElementById('fb-toast-msg');

    async function sendFeedback(userAgrees, correctedLabel = null) {
        if (!currentFilename) return;

        try {
            const res = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filename: currentFilename,
                    predicted_label: currentLabel,
                    user_agrees: userAgrees,
                    corrected_label: correctedLabel
                })
            });

            const data = await res.json();
            if (data.status === 'success') {
                fbToast.classList.remove('hidden');
                if (userAgrees) {
                    fbToastMsg.textContent = 'Feedback saved! Model active learning store confirmed prediction.';
                } else {
                    const finalLbl = data.entry.final_verified_label;
                    fbToastMsg.textContent = `Correction saved! Model override active: Image stored as ${finalLbl}. Future runs will remember this.`;
                    
                    // Update UI live to reflect human override
                    resultLabel.textContent = `${finalLbl} (HUMAN OVERRIDE)`;
                    resultBadge.className = finalLbl.includes('REAL') ? 'result-badge real' : 'result-badge fake';
                    badgeIcon.innerHTML = finalLbl.includes('REAL') ? '<i data-lucide="shield-check"></i>' : '<i data-lucide="shield-alert"></i>';
                    lucide.createIcons();
                }
            }
        } catch (err) {
            console.error('Error submitting feedback:', err);
        }
    }

    if (fbAgreeBtn) {
        fbAgreeBtn.addEventListener('click', () => sendFeedback(true));
    }

    if (fbDisagreeBtn) {
        fbDisagreeBtn.addEventListener('click', () => {
            const isCurrentlyFake = currentLabel ? currentLabel.includes('DEEPFAKE') : true;
            const targetLabel = isCurrentlyFake ? 'REAL' : 'LIKELY DEEPFAKE';
            const userChoice = confirm(`Override assessment for this image?\nClick OK to re-classify as: ${targetLabel}`);
            if (userChoice) {
                sendFeedback(false, targetLabel);
            }
        });
    }

    function triggerPdfDownload() {
        if (currentPdfUrl) {
            window.location.href = currentPdfUrl;
        } else {
            alert('PDF Report is generating. Please try again in a moment.');
        }
    }

    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const modalDownloadPdfBtn = document.getElementById('modal-download-pdf-btn');

    if (downloadPdfBtn) downloadPdfBtn.addEventListener('click', triggerPdfDownload);
    if (modalDownloadPdfBtn) modalDownloadPdfBtn.addEventListener('click', triggerPdfDownload);


    function showGradCamView() {
        modeOverlayBtn.classList.add('active');
        modeMeshBtn.classList.remove('active');
        modeSplitBtn.classList.remove('active');

        viewerOverlay.classList.remove('hidden');
        viewerSplit.classList.add('hidden');

        imgHeatmapOverlay.classList.remove('hidden');
        imgMeshOverlay.classList.add('hidden');
    }

    function showMeshView() {
        modeMeshBtn.classList.add('active');
        modeOverlayBtn.classList.remove('active');
        modeSplitBtn.classList.remove('active');

        viewerOverlay.classList.remove('hidden');
        viewerSplit.classList.add('hidden');

        imgMeshOverlay.classList.remove('hidden');
        imgHeatmapOverlay.classList.add('hidden');
    }

    function showSplitView() {
        modeSplitBtn.classList.add('active');
        modeOverlayBtn.classList.remove('active');
        modeMeshBtn.classList.remove('active');

        viewerSplit.classList.remove('hidden');
        viewerOverlay.classList.add('hidden');
    }

    // View Mode Toggle Listeners
    modeOverlayBtn.addEventListener('click', showGradCamView);
    modeMeshBtn.addEventListener('click', showMeshView);
    modeSplitBtn.addEventListener('click', showSplitView);

    // Opacity Slider Listener
    opacitySlider.addEventListener('input', (e) => {
        const val = e.target.value;
        opacityVal.textContent = `${val}%`;
        imgHeatmapOverlay.style.opacity = (val / 100).toString();
        imgMeshOverlay.style.opacity = (val / 100).toString();
    });


    // Reset UI
    function resetUI() {
        inputSection.classList.remove('hidden');
        heroSection.classList.remove('hidden');
        loadingSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        fileInput.value = '';
    }

    resetBtn.addEventListener('click', resetUI);

    // Verification Report Modal Logic
    viewReportBtn.addEventListener('click', () => {
        if (!currentReportData) return;

        repId.textContent = currentReportData.report_id;
        repTime.textContent = currentReportData.timestamp;
        repFilename.textContent = currentReportData.filename;
        repModel.textContent = `${currentReportData.model_name}`;
        repLabel.textContent = currentReportData.result_label;
        repConf.textContent = `${currentReportData.confidence_percentage}%`;

        const isFake = currentReportData.result_label.includes('DEEPFAKE');
        repResultBox.className = `rep-result-box ${isFake ? 'fake' : 'real'}`;

        repImgOrig.src = currentReportData.original_url;
        repImgHeat.src = currentReportData.heatmap_url;
        repDisclaimerText.textContent = currentReportData.disclaimer;

        reportModal.classList.remove('hidden');
        lucide.createIcons();
    });

    const closeReportModal = () => reportModal.classList.add('hidden');
    closeModalBtn.addEventListener('click', closeReportModal);
    modalCloseBtn.addEventListener('click', closeReportModal);

    printReportBtn.addEventListener('click', () => {
        window.print();
    });

    // Startup Init
    checkHealth();
    loadSamples();
});
