import os
import uuid
import shutil
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file

from backend.config import (
    BASE_DIR, UPLOADS_DIR, OUTPUTS_DIR, HEATMAPS_DIR, LANDMARKS_DIR, REPORTS_DIR, SAMPLES_DIR,
    FRONTEND_DIR, ALLOWED_EXTENSIONS
)
from backend.preprocessing import load_and_preprocess_image
from backend.predict import get_model, predict_image
from backend.gradcam import generate_gradcam
from backend.report import generate_report_data
from backend.pdf_report import build_pdf_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("deepguard.app")

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


def allowed_file(filename):
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET"])
def health_check():
    model_loaded = False
    try:
        get_model()
        model_loaded = True
    except Exception as e:
        logger.warning(f"Health check model load status: {e}")

    return jsonify({
        "status": "ok",
        "service": "DeepGuard Explainable Digital Image Verification",
        "model": "Xception",
        "model_loaded": model_loaded
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files and "sample_name" not in request.form:
        return jsonify({"error": "No image file or sample provided."}), 400

    file_stem = uuid.uuid4().hex[:10]

    if "sample_name" in request.form and request.form["sample_name"]:
        sample_name = request.form["sample_name"]
        sample_path = SAMPLES_DIR / sample_name
        if not sample_path.exists():
            return jsonify({"error": f"Sample image '{sample_name}' not found."}), 404
        
        target_filename = f"sample_{file_stem}_{sample_name}"
        saved_image_path = UPLOADS_DIR / target_filename
        shutil.copy(sample_path, saved_image_path)
    else:
        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "Selected image filename is empty."}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": f"Unsupported file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        ext = Path(file.filename).suffix.lower()
        target_filename = f"upload_{file_stem}{ext}"
        saved_image_path = UPLOADS_DIR / target_filename
        file.save(str(saved_image_path))

    try:
        # 1. Preprocess
        input_tensor, original_bgr, square_bgr = load_and_preprocess_image(saved_image_path)

        # 2. Predict (Hybrid Deep Learning + Boundary Morphing Signal Analysis + EXIF + Landmarks)
        raw_score, label, confidence_pct, exif_info, landmarks_info = predict_image(input_tensor, saved_image_path)

        # Check if morphing anomaly was flagged
        is_morphed = "MORPHED" in label

        # 3. Grad-CAM++ & Morph Seam Heatmap
        heatmap_url = generate_gradcam(input_tensor, original_bgr, file_stem, is_morphed=is_morphed)
        original_url = f"/uploads/{target_filename}"

        # 4. Landmark Overlay URL
        landmark_url = None
        mesh_abs_path = landmarks_info.get("mesh_overlay_path")
        if mesh_abs_path:
            mesh_filename = os.path.basename(mesh_abs_path)
            landmark_url = f"/outputs/landmarks/{mesh_filename}"

        # 5. Report Metadata
        report_data = generate_report_data(
            filename=target_filename,
            label=label,
            raw_score=raw_score,
            confidence_pct=confidence_pct,
            heatmap_url=heatmap_url,
            original_url=original_url
        )
        report_data["metadata"] = exif_info
        report_data["landmarks"] = landmarks_info

        # 6. Generate Formal PDF Report
        pdf_filename = f"report_{file_stem}.pdf"
        pdf_abs_path = REPORTS_DIR / pdf_filename
        heatmap_abs_path = HEATMAPS_DIR / f"heatmap_{file_stem}.jpg"
        build_pdf_report(
            report_data=report_data,
            original_img_path=str(saved_image_path),
            heatmap_path=str(heatmap_abs_path),
            mesh_path=str(mesh_abs_path) if mesh_abs_path else "",
            output_pdf_path=str(pdf_abs_path)
        )
        pdf_url = f"/api/download-report/{pdf_filename}"

        return jsonify({
            "status": "success",
            "filename": target_filename,
            "label": label,
            "raw_score": round(raw_score, 4),
            "confidence": round(confidence_pct, 1),
            "original_url": original_url,
            "heatmap_url": heatmap_url,
            "landmark_url": landmark_url,
            "pdf_url": pdf_url,
            "metadata": exif_info,
            "landmarks": landmarks_info,
            "report": report_data
        })

    except Exception as e:
        logger.error(f"Error processing image {saved_image_path}: {e}", exc_info=True)
        return jsonify({"error": f"Model inference error: {str(e)}"}), 500


from backend.feedback import record_user_feedback, get_verified_override

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(force=True, silent=True) or request.form
    filename = data.get("filename")
    predicted_label = data.get("predicted_label", "UNKNOWN")
    user_agrees = str(data.get("user_agrees", "true")).lower() in ["true", "1", "yes"]
    corrected_label = data.get("corrected_label")

    if not filename:
        return jsonify({"error": "Missing filename parameter."}), 400

    target_path = UPLOADS_DIR / filename
    if not target_path.exists():
        target_path = SAMPLES_DIR / filename

    entry = record_user_feedback(
        image_path=str(target_path),
        predicted_label=predicted_label,
        user_agrees=user_agrees,
        corrected_label=corrected_label
    )

    logger.info(f"Feedback recorded for {filename}: agrees={user_agrees}, final_label={entry['final_verified_label']}")

    return jsonify({
        "status": "success",
        "message": "Human feedback recorded in active learning store.",
        "entry": entry
    })




@app.route("/api/download-report/<path:filename>", methods=["GET"])
def download_pdf_report(filename):
    return send_from_directory(str(REPORTS_DIR), filename, as_attachment=True)



@app.route("/outputs/landmarks/<path:filename>")
def serve_landmarks(filename):
    return send_from_directory(str(LANDMARKS_DIR), filename)



@app.route("/api/samples", methods=["GET"])
def list_samples():
    samples = []
    if SAMPLES_DIR.exists():
        for f in SAMPLES_DIR.iterdir():
            if f.is_file() and allowed_file(f.name):
                # Infer real/fake label from filename convention if available
                is_fake = "fake" in f.name.lower() or "deepfake" in f.name.lower()
                samples.append({
                    "name": f.name,
                    "url": f"/samples/{f.name}",
                    "hint_label": "DEEPFAKE SAMPLE" if is_fake else "REAL SAMPLE"
                })
    return jsonify({"samples": samples})


# Serve static file routes
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(str(UPLOADS_DIR), filename)


@app.route("/outputs/heatmaps/<path:filename>")
def serve_heatmap(filename):
    return send_from_directory(str(HEATMAPS_DIR), filename)


@app.route("/samples/<path:filename>")
def serve_sample(filename):
    return send_from_directory(str(SAMPLES_DIR), filename)


@app.route("/")
def serve_index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
