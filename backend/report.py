import time
import random
from datetime import datetime

def generate_report_data(filename, label, raw_score, confidence_pct, heatmap_url, original_url):
    """
    Generates a structured report payload.
    """
    report_id = f"DG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    report_payload = {
        "report_id": report_id,
        "timestamp": timestamp,
        "filename": filename,
        "model_name": "Xception Deepfake Classifier",
        "benchmark_reference": "FaceForensics++ (TENCON 2024 Paper Benchmark: 97.52%)",
        "result_label": label,
        "raw_score": round(raw_score, 4),
        "confidence_percentage": round(confidence_pct, 1),
        "heatmap_url": heatmap_url,
        "original_url": original_url,
        "disclaimer": "This report provides AI-assisted verification based on neural network feature activation (Grad-CAM). It serves as an explainability screening tool and does not constitute certified legal or forensic proof."
    }

    return report_payload
