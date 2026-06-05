from typing import Any

import cv2
import numpy as np


def enhance_underwater_image(image: np.ndarray) -> np.ndarray:
    """
    Apply simple preprocessing to improve underwater visibility before object detection.

    This reduces noise with a gentle Gaussian blur and slightly boosts contrast/brightness
    so structures and targets are more distinguishable for the detector.
    """
    if image is None:
        return image

    enhanced = cv2.GaussianBlur(image, (5, 5), 0)
    enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=10)

    # Added CLAHE contrast enhancement
    lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    return enhanced

