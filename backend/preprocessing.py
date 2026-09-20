import cv2
import numpy as np
from PIL import Image
from backend.config import IMAGE_SIZE

def make_square(img_bgr):
    """
    Pads an image with border padding to make it square without distorting aspect ratio.
    """
    h, w = img_bgr.shape[:2]
    if h == w:
        return img_bgr

    max_dim = max(h, w)
    top = (max_dim - h) // 2
    bottom = max_dim - h - top
    left = (max_dim - w) // 2
    right = max_dim - w - left

    # Black border padding
    square_img = cv2.copyMakeBorder(img_bgr, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    return square_img


def load_and_preprocess_image(image_path):
    """
    Loads an image from file path and preprocesses it for model inference.
    Convert to RGB -> square letterbox -> resize (224, 224) -> scale to [0, 1].
    Returns:
        input_tensor: numpy array of shape (1, 224, 224, 3)
        original_bgr: original BGR image
        square_bgr: square padded BGR image
    """
    original_bgr = cv2.imread(str(image_path))
    if original_bgr is None:
        pil_img = Image.open(str(image_path)).convert('RGB')
        original_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    square_bgr = make_square(original_bgr)
    
    # Convert BGR to RGB for deep learning model input
    square_rgb = cv2.cvtColor(square_bgr, cv2.COLOR_BGR2RGB)
    resized_rgb = cv2.resize(square_rgb, IMAGE_SIZE)
    normalized_image = resized_rgb.astype(np.float32) / 255.0
    input_tensor = np.expand_dims(normalized_image, axis=0)

    return input_tensor, original_bgr, square_bgr
