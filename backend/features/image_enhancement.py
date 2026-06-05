def enhance_underwater_image(image: np.ndarray) -> np.ndarray:
    """
    Apply preprocessing to improve underwater visibility before object detection.
    Steps:
    1. Denoise with Gaussian blur
    2. CLAHE for adaptive contrast enhancement (handles uneven lighting underwater)
    3. White balance correction (removes the blue/green color cast underwater)
    4. Brightness/contrast boost
    """
    if image is None:
        return image

    # Step 1: Denoise
    enhanced = cv2.GaussianBlur(image, (5, 5), 0)

    # Step 2: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # Applied per channel in LAB color space so color isn't distorted
    lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # Step 3: White balance (gray world assumption)
    # Underwater images have a heavy blue/green cast; this corrects it
    b_channel, g_channel, r_channel = cv2.split(enhanced.astype(np.float32))
    mean_b, mean_g, mean_r = np.mean(b_channel), np.mean(g_channel), np.mean(r_channel)
    overall_mean = (mean_b + mean_g + mean_r) / 3
    b_channel = np.clip(b_channel * (overall_mean / mean_b), 0, 255)
    g_channel = np.clip(g_channel * (overall_mean / mean_g), 0, 255)
    r_channel = np.clip(r_channel * (overall_mean / mean_r), 0, 255)
    enhanced = cv2.merge([b_channel, g_channel, r_channel]).astype(np.uint8)

    # Step 4: Brightness and contrast boost
    enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=10)

    return enhanced
