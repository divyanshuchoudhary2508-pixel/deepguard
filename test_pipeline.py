import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.preprocessing import load_and_preprocess_image
from backend.predict import predict_image
from backend.gradcam import generate_gradcam
from backend.report import generate_report_data

def test_full_pipeline():
    print("=== Testing DeepGuard Inference & Grad-CAM Pipeline ===")
    sample_path = root_dir / "samples" / "Rashmika_Mandanna.jpg"
    if not sample_path.exists():
        print(f"Sample file {sample_path} does not exist.")
        return False

    print(f"1. Loading & preprocessing {sample_path.name}...")
    input_tensor, original_bgr, resized_bgr = load_and_preprocess_image(sample_path)
    print("   Input tensor shape:", input_tensor.shape)

    print("2. Running model prediction...")
    raw_score, label, confidence_pct = predict_image(input_tensor)
    print(f"   Raw Score: {raw_score:.4f} | Label: {label} | Confidence: {confidence_pct:.1f}%")

    print("3. Generating Grad-CAM heatmap...")
    heatmap_url = generate_gradcam(input_tensor, original_bgr, "test_run")
    print(f"   Generated Heatmap URL: {heatmap_url}")

    print("4. Generating Report Payload...")
    report = generate_report_data("test_run.jpg", label, raw_score, confidence_pct, heatmap_url, "/uploads/test_run.jpg")
    print(f"   Report ID: {report['report_id']}")

    print("\nSUCCESS! All components verified.")
    return True

if __name__ == "__main__":
    test_full_pipeline()
