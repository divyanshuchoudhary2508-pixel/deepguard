# DeepGuard — Explainable Deepfake Detection Platform

<div align="center">

![DeepGuard Banner](https://img.shields.io/badge/DeepGuard-AI%20Forensics-1A6EFF?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST%20API-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00C48C?style=for-the-badge)
![Research](https://img.shields.io/badge/IEEE%20TENCON-2024%20Research-0068A5?style=for-the-badge&logo=ieee&logoColor=white)

**"See Through the Fake. Protect What's Real."**

*The world's first multi-signal, explainable deepfake forensics platform.*  
*Built on peer-reviewed IEEE TENCON 2024 research.*

[Live Demo](#usage) · [API Docs](#api-reference) · [Research Paper](#research-foundation) · [Report Issues](https://github.com/divyanshuchoudhary25/deepguard/issues)

</div>

---

## What is DeepGuard?

DeepGuard is **not just another deepfake detector**. While most tools give you a binary `FAKE / REAL` verdict with zero explanation, DeepGuard produces a full **multi-signal forensic audit** — combining 5 independent detection layers, neural attention heatmaps, facial geometry analysis, and cryptographic evidence — all packaged into a **court-admissible Forensic Verification PDF Report**.

### The Problem with Existing Tools
- 🔴 **Black-box verdicts** — no explanation, legally inadmissible
- 🔴 **Single neural network** — high false-positive rate on edge cases
- 🔴 **No cryptographic proof** — no chain-of-custody for legal proceedings
- 🔴 **No human correction** — models hallucinate, no way to fix them

### The DeepGuard Solution
- ✅ **6-layer multi-signal analysis** — neural + physical forensics
- ✅ **Grad-CAM++ heatmaps** — shows *exactly* which facial region triggered the AI
- ✅ **SHA-256 cryptographic hash** — links the image to the report permanently
- ✅ **Active learning override** — human experts can correct and lock verdicts forever
- ✅ **PDF Forensic Report** — timestamped, court-style evidence document

---

## Screenshots

| Web Dashboard | Analysis Result | Forensic PDF |
|:---:|:---:|:---:|
| Glassmorphism UI with drag-and-drop | Grad-CAM++ heatmap + confidence gauge | SHA-256 anchored evidence report |

---

## Features

### 🧠 Multi-Signal Forensic Engine

| Signal | What It Detects | Technology |
|:---|:---|:---|
| **DenseNet121 Neural Map** | Micro-facial pattern anomalies, skin warping | Transfer Learning + Grad-CAM++ |
| **2D Fourier FFT Analysis** | High-freq power loss (GAN/Diffusion fingerprint) | NumPy FFT, SciPy |
| **Head-Body Laplacian Seam** | Face-swap splicing boundary artefacts | OpenCV Laplacian |
| **EXIF & C2PA Metadata** | AI software signatures, missing camera data | piexif |
| **68-Point Facial Geometry** | Eye asymmetry, jawline warp, landmark count | MediaPipe |
| **Active Learning Engine** | Human-corrected verdicts locked by SHA-256 | hashlib + JSON store |

### 📊 Output for Every Scan
- Calibrated probability score (`0.00 → 1.00`)
- Grad-CAM++ neural attention heatmap overlay
- 68-point facial mesh visualization
- Full EXIF metadata card
- Downloadable **Forensic Verification PDF Report**

### 🌐 REST API
Full API access for B2B integration — drop DeepGuard into any existing KYC, compliance, or content moderation pipeline.

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/divyanshuchoudhary25/deepguard.git
cd deepguard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your trained model weights
# Place your model.h5 in:
# DeepFake-Detection-main/Models/model.h5
# (See Training section to train your own)

# 4. Start the server
python run_server.py
```

Open your browser at **http://127.0.0.1:5000** 🚀

---

## Training Your Own Model

DeepGuard uses a **DenseNet121** backbone trained on 40,000+ real/fake face images using 2-phase transfer learning on **2× NVIDIA Tesla T4 GPUs**.

### Using Kaggle (Recommended — Free GPU)

```bash
# 1. Set up Kaggle API credentials
# Place kaggle.json in C:\Users\<you>\.kaggle\

# 2. Generate the training notebook
python create_kaggle_kernel.py

# 3. Push to Kaggle (runs on 2x T4 GPU)
kaggle kernels push -p .

# 4. Monitor training
kaggle kernels status divyanshuchoudhary25/deepguard-densenet121-t4x2

# 5. Download trained model when complete
kaggle kernels output divyanshuchoudhary25/deepguard-densenet121-t4x2 -p ./DeepFake-Detection-main/Models
```

### Training Datasets Used
- [`manjilkarki/deepfake-and-real-images`](https://www.kaggle.com/datasets/manjilkarki/deepfake-and-real-images) — 20,000+ images
- [`dagnelies/deepfake-faces`](https://www.kaggle.com/datasets/dagnelies/deepfake-faces) — 20,000+ images

### Training Architecture
```
Phase 1: Frozen DenseNet121 backbone
         Adam lr=1e-3 | 10 epochs | Batch=32
         GlobalAveragePooling → BatchNorm → Dropout(0.4) → Dense(256, ReLU) → Dense(1, Sigmoid)

Phase 2: Unfreeze top 30 layers
         Adam lr=1e-5 | 10 epochs | Batch=32
         Mixed FP16 precision | MirroredStrategy (2x GPU)
```

---

## API Reference

Base URL: `http://127.0.0.1:5000`

### `POST /api/predict`
Upload an image for full forensic analysis.

**Request**
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -F "image=@path/to/face.jpg"
```

**Response**
```json
{
  "label": "DEEPFAKE DETECTED",
  "confidence": 94.7,
  "raw_score": 0.947,
  "sha256": "a3f9b2c1...",
  "gradcam_image": "data:image/png;base64,...",
  "mesh_image": "data:image/png;base64,...",
  "exif": { "Make": null, "Software": "Midjourney" },
  "fft_score": 0.61,
  "seam_score": 0.83,
  "landmark_count": 68,
  "eye_symmetry": 0.92,
  "report_url": "/api/download-report/report_face.pdf"
}
```

### `GET /api/health`
```json
{ "status": "ok", "model": "Xception", "model_loaded": true }
```

### `POST /api/feedback`
Submit expert correction for active learning.
```bash
curl -X POST http://127.0.0.1:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"sha256": "a3f9b2c1...", "agreed": false, "override_label": "AUTHENTIC"}'
```

### `GET /api/download-report/<filename>`
Download the forensic PDF report.

### `GET /api/samples`
List pre-loaded sample images.

---

## Project Structure

```
deepguard/
├── backend/
│   ├── app.py              # Flask REST API & routes
│   ├── predict.py          # DenseNet121 inference engine
│   ├── gradcam.py          # Grad-CAM++ heatmap generation
│   ├── landmarks.py        # MediaPipe 68-point facial mesh
│   ├── metadata.py         # EXIF / C2PA inspector
│   ├── preprocessing.py    # Image normalization pipeline
│   ├── feedback.py         # Active learning SHA-256 engine
│   ├── pdf_report.py       # ReportLab forensic PDF generator
│   ├── report.py           # Report utilities
│   └── config.py           # Paths and configuration
├── frontend/
│   ├── index.html          # Glassmorphism web dashboard
│   ├── script.js           # UI logic, API calls, Grad-CAM display
│   └── style.css           # Premium dark glassmorphism design
├── samples/                # Pre-loaded sample images
├── uploads/                # Temporary upload storage (git-ignored)
├── outputs/                # Generated reports (git-ignored)
├── DeepGuard_Kaggle_T4x2_Training.ipynb  # Kaggle training notebook
├── create_kaggle_kernel.py # Kaggle notebook generator
├── kaggle_train.py         # Training pipeline script
├── generate_pitch_pdf.py   # Startup pitch PDF generator
├── run_server.py           # Server entry point
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Research Foundation

DeepGuard is built on the methodology from:

> **"Deepfake Detection in Digital Images using Data Augmentation and Layer Unfreezing across Various Deep Learning Models"**  
> Reshma Sunil, Parita Mer, Anjali Diwan, Parth Parmar  
> **IEEE TENCON 2024** — IEEE Region 10 Conference  
> Marwadi University, Rajkot, India

### Paper → Product Mapping

| Paper Finding | DeepGuard Implementation |
|:---|:---|
| DenseNet121 achieves highest accuracy across 5 models | DenseNet121 selected as primary backbone |
| 2-phase unfreezing improves fine-tuning by 11.2% | Phase 1 (frozen) + Phase 2 (top 30 layers unfrozen) |
| Data augmentation reduces overfitting | RandomFlip, RandomRotation, RandomZoom in Keras graph |
| Grad-CAM improves expert trust in decisions | Sharpened Grad-CAM++ overlaid on original image |

### Extensions Beyond the Paper
DeepGuard extends the academic detection model into a **production forensics platform** by adding:
- 5-layer multi-signal physical forensics (FFT, Laplacian, EXIF, Mesh)
- SHA-256 cryptographic evidence chain
- Active learning human override engine
- Enterprise PDF forensic report generation
- Full REST API for B2B integration

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| Backend | Python 3.12, Flask, TensorFlow 2.20, OpenCV |
| AI/ML | DenseNet121, MediaPipe, Grad-CAM++, NumPy, SciPy |
| Forensics | piexif, ReportLab, hashlib SHA-256 |
| Frontend | Vanilla JS, CSS3 Glassmorphism, Lucide Icons |
| Training | Kaggle 2× T4 GPU, MirroredStrategy, Mixed FP16 |

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Author

**Divyanshu Choudhary**  
[![Kaggle](https://img.shields.io/badge/Kaggle-divyanshuchoudhary25-20BEFF?style=flat&logo=kaggle)](https://www.kaggle.com/divyanshuchoudhary25)
[![GitHub](https://img.shields.io/badge/GitHub-divyanshuchoudhary25-181717?style=flat&logo=github)](https://github.com/divyanshuchoudhary25)

---

<div align="center">

*Built on Science. Designed for the Courtroom. Ready for the Enterprise.*

⭐ **Star this repo if you find it useful!** ⭐

</div>
