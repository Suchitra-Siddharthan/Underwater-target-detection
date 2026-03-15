"""
Detection Heatmap Feature - Generate heatmaps showing detection concentrations
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any
from fastapi import HTTPException


def generate_detection_heatmap(
    image: np.ndarray,
    detections: list,
    heatmap_size: Tuple[int, int] = (256, 256)
) -> Dict[str, Any]:
    """
    Generate a detection heatmap by tracking detection density across image regions

    Args:
        image: Original image as numpy array (BGR format)
        detections: Object detection results from YOLO:
                   [
                       {"box": [x1, y1, x2, y2], "class": "class_name", "confidence": 0.95},
                       ...
                   ]
                   Box coordinates should be normalized or in pixel coordinates

        heatmap_size: Size of the heatmap grid. Default (256, 256)

    Returns:
        Dict containing:
        - heatmap_image: Overlay heatmap on original image (for visualization)
        - heatmap_data: Normalized heatmap matrix (0-255, for analysis)
        - detection_centers: List of center points where detections occurred
        - heatmap_intensity_map: Raw intensity values before normalization

    Note:
        This function works with detection regions, not just bounding boxes.
        If bounding box info is not in detections, uses full image.
    """
    try:
        if image is None:
            raise ValueError("Image cannot be None")

        img_height, img_width = image.shape[:2]

        # Initialize heatmap
        heatmap = np.zeros((heatmap_size[1], heatmap_size[0]), dtype=np.float32)
        detection_centers = []

        # Calculate scaling factors
        scale_x = heatmap_size[0] / img_width if img_width > 0 else 1
        scale_y = heatmap_size[1] / img_height if img_height > 0 else 1

        # If detections have bounding boxes, use their centers as detection points
        if detections and isinstance(detections[0], dict) and "box" in detections[0]:
            for detection in detections:
                box = detection.get("box", [])
                if len(box) >= 4:
                    # Calculate center of bounding box
                    x1, y1, x2, y2 = box[:4]
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2

                    # Convert to heatmap coordinates
                    hm_x = int(center_x * scale_x)
                    hm_y = int(center_y * scale_y)

                    # Ensure coordinates are within bounds
                    hm_x = max(0, min(hm_x, heatmap_size[0] - 1))
                    hm_y = max(0, min(hm_y, heatmap_size[1] - 1))

                    detection_centers.append((center_x, center_y))

                    # Add gaussian blur around detection center for smoother heatmap
                    cv2.circle(heatmap, (hm_x, hm_y), radius=5, color=1.0, thickness=-1)
        else:
            # If no bounding box info, add a point at image center for each detection
            center_x = img_width / 2
            center_y = img_height / 2
            hm_x = int(center_x * scale_x)
            hm_y = int(center_y * scale_y)

            for _ in detections:
                detection_centers.append((center_x, center_y))
                cv2.circle(heatmap, (hm_x, hm_y), radius=5, color=1.0, thickness=-1)

        # Apply Gaussian blur for smooth transitions
        heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)

        # Normalize heatmap to 0-255 range
        if heatmap.max() > 0:
            heatmap_normalized = (heatmap / heatmap.max() * 255).astype(np.uint8)
        else:
            heatmap_normalized = heatmap.astype(np.uint8)

        # Apply colormap to visualize heatmap
        heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)

        # Resize colored heatmap to original image size
        heatmap_colored = cv2.resize(
            heatmap_colored,
            (img_width, img_height),
            interpolation=cv2.INTER_LINEAR
        )

        # Blend heatmap with original image (50% transparency for visibility)
        alpha = 0.4  # Transparency of heatmap
        heatmap_overlay = cv2.addWeighted(
            image,
            1 - alpha,
            heatmap_colored,
            alpha,
            0
        )

        return {
            "heatmap_image": heatmap_overlay,
            "heatmap_data": heatmap_normalized,
            "detection_centers": detection_centers,
            "heatmap_intensity_map": heatmap,
            "num_detections": len(detections),
            "heatmap_size": heatmap_size
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate heatmap: {str(e)}"
        )


def get_heatmap_statistics(heatmap_data: np.ndarray) -> Dict[str, Any]:
    """
    Calculate statistics about the heatmap

    Args:
        heatmap_data: Normalized heatmap matrix (0-255)

    Returns:
        Dict containing:
        - max_intensity: Brightest point in heatmap
        - min_intensity: Dimmest point in heatmap
        - mean_intensity: Average intensity
        - detection_density: Percentage of non-zero pixels
    """
    non_zero = np.count_nonzero(heatmap_data)
    total_pixels = heatmap_data.size

    return {
        "max_intensity": int(heatmap_data.max()),
        "min_intensity": int(heatmap_data.min()),
        "mean_intensity": float(heatmap_data.mean()),
        "detection_density": float((non_zero / total_pixels) * 100) if total_pixels > 0 else 0.0
    }


def get_hotspot_regions(
    heatmap_data: np.ndarray,
    threshold_percentile: int = 75
) -> list:
    """
    Identify hotspot regions where detections are concentrated

    Args:
        heatmap_data: Normalized heatmap matrix (0-255)
        threshold_percentile: Percentile threshold for hotspots (0-100)

    Returns:
        List of hotspot regions with their intensity levels
    """
    threshold = np.percentile(heatmap_data, threshold_percentile)

    # Find pixels above threshold
    hotspots = np.where(heatmap_data > threshold)

    if len(hotspots[0]) == 0:
        return []

    # Group consecutive hotspot pixels
    hotspot_regions = []
    visited = set()

    for i in range(len(hotspots[0])):
        y, x = hotspots[1][i], hotspots[0][i]

        if (x, y) not in visited:
            # Found a new hotspot region
            region = {
                "center_x": int(x),
                "center_y": int(y),
                "intensity": int(heatmap_data[y, x])
            }
            hotspot_regions.append(region)
            visited.add((x, y))

    return hotspot_regions
