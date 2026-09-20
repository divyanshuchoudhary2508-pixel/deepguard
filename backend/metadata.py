"""
EXIF Metadata & Digital Signature Forensic Inspector for DeepGuard.
Extracts camera metadata, editing software signatures, C2PA digital credentials,
and assesses metadata risk level.
"""

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

AI_SOFTWARE_KEYWORDS = [
    "firefly", "generative fill", "midjourney", "stable diffusion",
    "dall-e", "dalle", "comfyui", "automatic1111", "fooocus", "flux",
    "kling", "runway", "pika", "sora", "canva ai", "novelai", "starryai"
]

CAMERA_MAKES = [
    "canon", "nikon", "sony", "apple", "samsung", "fujifilm", "panasonic",
    "olympus", "leica", "google", "xiaomi", "oneplus", "huawei", "hasselblad"
]


def extract_exif_metadata(image_path: str) -> dict:
    """
    Extract EXIF tags, software signatures, and C2PA markers from image file.
    Returns structured metadata report dictionary.
    """
    result = {
        "has_exif": False,
        "camera_make": "Unknown / None",
        "camera_model": "Unknown / None",
        "software": "None detected",
        "date_taken": "N/A",
        "ai_signatures_found": [],
        "c2pa_credentials": False,
        "metadata_risk_level": "STRIPPED_UNVERIFIED",
        "risk_explanation": "Image metadata was stripped or missing (common in web/social media uploads).",
        "raw_tags": {}
    }

    if not os.path.exists(image_path):
        return result

    try:
        # Check raw binary for C2PA or XMP digital credentials markers
        with open(image_path, "rb") as f:
            content = f.read()
            lower_content = content.lower()
            if b"c2pa" in lower_content or b"jumbf" in lower_content or b"contentcredentials" in lower_content:
                result["c2pa_credentials"] = True

            for kw in AI_SOFTWARE_KEYWORDS:
                if kw.encode('utf-8') in lower_content:
                    if kw not in result["ai_signatures_found"]:
                        result["ai_signatures_found"].append(kw.upper())

        # PIL EXIF extraction
        img = Image.open(image_path)
        exif_data = img._getexif()

        if exif_data:
            result["has_exif"] = True
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                
                # Format string values
                if isinstance(value, bytes):
                    try:
                        val_str = value.decode('utf-8', errors='ignore').strip('\x00')
                    except Exception:
                        val_str = str(value)
                else:
                    val_str = str(value)

                result["raw_tags"][str(tag_name)] = val_str[:100]

                tag_lower = str(tag_name).lower()
                val_lower = val_str.lower()

                if tag_lower == "make":
                    result["camera_make"] = val_str
                elif tag_lower == "model":
                    result["camera_model"] = val_str
                elif tag_lower == "software":
                    result["software"] = val_str
                elif tag_lower in ["datetimeoriginal", "datetime"]:
                    result["date_taken"] = val_str

                # Check for AI keywords in tag values
                for kw in AI_SOFTWARE_KEYWORDS:
                    if kw in val_lower:
                        if kw.upper() not in result["ai_signatures_found"]:
                            result["ai_signatures_found"].append(kw.upper())

        # Metadata Risk Level Logic
        if result["ai_signatures_found"] or (result["c2pa_credentials"] and "firefly" in str(result["raw_tags"]).lower()):
            result["metadata_risk_level"] = "AI_GENERATED_SOFTWARE"
            result["risk_explanation"] = f"Generative AI signatures detected in metadata ({', '.join(result['ai_signatures_found'])})."
        elif any(make in result["camera_make"].lower() for make in CAMERA_MAKES):
            result["metadata_risk_level"] = "AUTHENTIC_HARDWARE"
            result["risk_explanation"] = f"Authentic camera hardware metadata present ({result['camera_make']} {result['camera_model']})."
        elif result["software"] != "None detected":
            result["metadata_risk_level"] = "EDITED_SOFTWARE"
            result["risk_explanation"] = f"Processed by image editing software ({result['software']}) without camera hardware EXIF."
        elif result["has_exif"]:
            result["metadata_risk_level"] = "GENERIC_EXIF"
            result["risk_explanation"] = "EXIF tags present but missing primary camera hardware identifier."
        else:
            result["metadata_risk_level"] = "STRIPPED_UNVERIFIED"
            result["risk_explanation"] = "Metadata stripped or absent. Common for compressed web/messaging uploads."

    except Exception as e:
        result["risk_explanation"] = f"Metadata inspection completed with notice: {str(e)}"

    return result
