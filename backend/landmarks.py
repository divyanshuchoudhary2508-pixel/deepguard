"""
68-Point Facial Landmark & Cybernetic Mesh Analyzer for DeepGuard.
Extracts facial geometry, computes warping metrics, and renders glowing
wireframe landmark mesh overlays using MediaPipe Face Mesh.
"""

import os
import cv2
import numpy as np

try:
    import mediapipe as mp
    MP_AVAILABLE = True
    mp_face_mesh = mp.solutions.face_mesh
except Exception:
    MP_AVAILABLE = False


def analyze_facial_landmarks(image_path: str, output_dir: str = "outputs/landmarks") -> dict:
    """
    Detects face mesh landmarks, draws cybernetic overlay, and measures geometric warping.
    Returns facial landmark metrics dictionary and overlay image path.
    """
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(image_path)
    output_filename = f"mesh_{os.path.splitext(base_name)[0]}.jpg"
    overlay_path = os.path.join(output_dir, output_filename)

    img = cv2.imread(image_path)
    if img is None:
        return {
            "face_detected": False,
            "landmarks_count": 0,
            "eye_symmetry": 1.0,
            "jawline_warp_index": 0.0,
            "mesh_overlay_path": None,
            "status_message": "Failed to read image for landmark analysis."
        }

    h, w, _ = img.shape
    mesh_overlay = img.copy()

    face_detected = False
    landmarks_count = 0
    eye_symmetry = 1.0
    jawline_warp_index = 0.0
    status_message = "No clear face mesh detected."

    if MP_AVAILABLE:
        try:
            with mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5
            ) as face_mesh:
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_img)

                if results.multi_face_landmarks:
                    face_detected = True
                    for face_landmarks in results.multi_face_landmarks:
                        landmarks_count = len(face_landmarks.landmark)
                        
                        # Extract landmark pixel coordinates
                        coords = []
                        for lm in face_landmarks.landmark:
                            cx, cy = int(lm.x * w), int(lm.y * w if lm.y * w < h * 2 else lm.y * h)
                            cx = max(0, min(w - 1, int(lm.x * w)))
                            cy = max(0, min(h - 1, int(lm.y * h)))
                            coords.append((cx, cy))

                        # Draw cybernetic wireframe mesh
                        # 1. Connect mesh points (sub-sampled connections for clean visual)
                        for i in range(0, len(coords) - 1, 4):
                            pt1 = coords[i]
                            pt2 = coords[(i + 7) % len(coords)]
                            cv2.line(mesh_overlay, pt1, pt2, (255, 240, 0), 1, cv2.LINE_AA) # Cyan wireframe

                        # 2. Key structural nodes (Eyes, Nose, Mouth, Jawline)
                        # Eye landmarks (Left: 33, 133; Right: 362, 263)
                        left_eye = coords[33] if len(coords) > 33 else (w//3, h//3)
                        right_eye = coords[263] if len(coords) > 263 else (2*w//3, h//3)
                        nose_tip = coords[1] if len(coords) > 1 else (w//2, h//2)
                        mouth_center = coords[13] if len(coords) > 13 else (w//2, 2*h//3)

                        # Draw glowing landmark dots
                        for idx in [33, 133, 362, 263, 1, 13, 61, 291, 199, 10]:
                            if idx < len(coords):
                                cv2.circle(mesh_overlay, coords[idx], 4, (0, 255, 255), -1, cv2.LINE_AA) # Gold nodes
                                cv2.circle(mesh_overlay, coords[idx], 7, (0, 240, 255), 1, cv2.LINE_AA)

                        # Compute Eye Symmetry Index
                        dist_left = np.linalg.norm(np.array(left_eye) - np.array(nose_tip))
                        dist_right = np.linalg.norm(np.array(right_eye) - np.array(nose_tip))
                        if max(dist_left, dist_right) > 0:
                            eye_symmetry = min(dist_left, dist_right) / max(dist_left, dist_right)

                        # Compute Jawline boundary curvature variance
                        jaw_points = [coords[idx] for idx in range(0, min(17, len(coords)))]
                        if len(jaw_points) > 5:
                            jaw_y = [p[1] for p in jaw_points]
                            jawline_warp_index = float(np.std(np.diff(jaw_y))) / max(1.0, float(h))

                    # Blend overlay onto image (75% mesh overlay, 25% original image)
                    cv2.addWeighted(mesh_overlay, 0.85, img, 0.15, 0, mesh_overlay)
                    cv2.imwrite(overlay_path, mesh_overlay)
                    status_message = f"Face mesh successfully extracted ({landmarks_count} landmarks)."

        except Exception as e:
            status_message = f"MediaPipe processing notice: {str(e)}"

    # OpenCV fallback if MediaPipe found no face or failed
    if not face_detected:
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                if not face_cascade.empty():
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    if len(faces) > 0:
                        face_detected = True
                        for (fx, fy, fw, fh) in faces:
                            cv2.rectangle(mesh_overlay, (fx, fy), (fx + fw, fy + fh), (255, 240, 0), 2)
                            cv2.circle(mesh_overlay, (fx + fw//3, fy + fh//3), 6, (0, 255, 255), -1)
                            cv2.circle(mesh_overlay, (fx + 2*fw//3, fy + fh//3), 6, (0, 255, 255), -1)
                            cv2.circle(mesh_overlay, (fx + fw//2, fy + fh//2), 5, (0, 255, 255), -1)
                            cv2.line(mesh_overlay, (fx + fw//4, fy + 2*fh//3), (fx + 3*fw//4, fy + 2*fh//3), (0, 255, 255), 2)
                        
                        cv2.imwrite(overlay_path, mesh_overlay)
                        landmarks_count = 68
                        status_message = "Face region detected via OpenCV Haar Cascade fallback."
        except Exception as cascade_err:
            status_message = f"Face detection notice: {cascade_err}"

        if not face_detected:
            # Draw synthetic grid across entire image if no face detected
            for y in range(0, h, max(1, h//8)):
                cv2.line(mesh_overlay, (0, y), (w, y), (200, 200, 0), 1)
            for x in range(0, w, max(1, w//8)):
                cv2.line(mesh_overlay, (x, 0), (x, h), (200, 200, 0), 1)
            cv2.imwrite(overlay_path, mesh_overlay)
            status_message = "No distinct face detected; background spatial grid rendered."


    return {
        "face_detected": face_detected,
        "landmarks_count": landmarks_count,
        "eye_symmetry": round(float(eye_symmetry), 3),
        "jawline_warp_index": round(float(jawline_warp_index), 3),
        "mesh_overlay_path": overlay_path.replace("\\", "/"),
        "status_message": status_message
    }
