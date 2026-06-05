from collections import Counter
from typing import List, Dict
import cv2


def generate_marine_summary(detections: List[Dict], image=None) -> str:
   
    species_classes = ["echinus", "holothurian", "scallop", "starfish"]

    counts = Counter(d.get("class") for d in detections if isinstance(d, dict) and d.get("class") in species_classes)

    total = sum(counts.values())

    if total == 0:
        summary = "No marine organisms detected in the image."
    else:
        dominant = max(counts, key=counts.get) if counts else None
        # Build the counts string
        count_parts = [f"{count} {species}" for species, count in counts.items() if count > 0]
        if len(count_parts) > 1:
            counts_str = ", ".join(count_parts[:-1]) + " and " + count_parts[-1]
        elif count_parts:
            counts_str = count_parts[0]
        else:
            counts_str = ""
        summary = f"The image reveals {counts_str} (total: {total} organisms), indicating a {dominant}-dominant underwater environment. This suggests a region with active benthic marine life."

    # Return only the core summary text (UI already provides the heading)
    return summary

