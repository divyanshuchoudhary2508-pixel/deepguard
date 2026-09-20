import os
from pathlib import Path

# Base Directory of deepguard
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
MODEL_PATH = BASE_DIR.parent / "DeepFake-Detection-main" / "Models" / "model.h5"
ALT_MODEL_PATH = BASE_DIR.parent / "DeepFake-Detection-main" / "Models" / "xception_deepfake_image.h5"

UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
HEATMAPS_DIR = OUTPUTS_DIR / "heatmaps"
LANDMARKS_DIR = OUTPUTS_DIR / "landmarks"
REPORTS_DIR = OUTPUTS_DIR / "reports"
SAMPLES_DIR = BASE_DIR / "samples"
FRONTEND_DIR = BASE_DIR / "frontend"

# Ensure directories exist
for d in [UPLOADS_DIR, OUTPUTS_DIR, HEATMAPS_DIR, LANDMARKS_DIR, REPORTS_DIR, SAMPLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)



# Image settings
IMAGE_SIZE = (224, 224)
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
PREDICTION_THRESHOLD = 0.5
