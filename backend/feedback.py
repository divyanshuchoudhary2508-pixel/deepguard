"""
Human-in-the-Loop Feedback & Active Learning Store for DeepGuard.
Stores user corrections, calculates hash signatures, and maintains an active learning dataset.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from backend.config import BASE_DIR

FEEDBACK_FILE = BASE_DIR / "feedback_dataset.json"


def load_feedback_db() -> dict:
    """Loads existing feedback database or initializes a new one."""
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"feedback_entries": {}, "summary": {"total_feedback": 0, "correct_predictions": 0, "user_overrides": 0}}


def compute_image_hash(image_path: str) -> str:
    """Computes SHA-256 hash of image file for fast lookup."""
    if not os.path.exists(image_path):
        return ""
    sha = hashlib.sha256()
    with open(image_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def record_user_feedback(image_path: str, predicted_label: str, user_agrees: bool, corrected_label: str = None) -> dict:
    """
    Records user feedback for an image.
    If user disagrees, stores the corrected label so the system learns immediately and prevents future false predictions.
    """
    db = load_feedback_db()
    file_hash = compute_image_hash(image_path)
    filename = os.path.basename(image_path)

    final_label = predicted_label if user_agrees else (corrected_label or ("REAL" if "DEEPFAKE" in predicted_label else "LIKELY DEEPFAKE"))

    entry = {
        "filename": filename,
        "hash": file_hash,
        "predicted_label": predicted_label,
        "user_agrees": user_agrees,
        "final_verified_label": final_label,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    # Store entry by hash and by filename
    db["feedback_entries"][file_hash] = entry
    db["feedback_entries"][filename] = entry

    # Update summary stats
    db["summary"]["total_feedback"] += 1
    if user_agrees:
        db["summary"]["correct_predictions"] += 1
    else:
        db["summary"]["user_overrides"] += 1

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

    return entry


def get_verified_override(image_path: str) -> dict:
    """
    Checks if an image has a verified human feedback override in the store.
    Returns override dictionary if found, else None.
    """
    db = load_feedback_db()
    file_hash = compute_image_hash(image_path)
    filename = os.path.basename(image_path)

    if file_hash in db["feedback_entries"]:
        return db["feedback_entries"][file_hash]
    if filename in db["feedback_entries"]:
        return db["feedback_entries"][filename]

    return None
