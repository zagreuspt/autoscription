from typing import List

import cv2
import numpy as np
from PIL import Image

from src.autoscription.core.logging import Monitoring


# do not iterate and modify the same list, use second list or filter instead
def remove_small_stamps(predictions: List[List[int]], image: Image, area_ratio_threshold: float) -> None:
    iw, ih = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).shape[::-1]
    image_area = iw * ih
    to_be_removed = []
    for box in predictions:
        w = int(box[2]) - int(box[0])
        h = int(box[3]) - int(box[1])
        area = w * h
        area_ratio = area / image_area
        if area_ratio < area_ratio_threshold:
            to_be_removed.append(box)
    for item in to_be_removed:
        predictions.remove(item)


def calculate_black_pixel_percentage(
    image: Image, predictions: List[List[List[int]]], binary_threshold_value: float, monitoring: Monitoring
) -> float:
    # Set the threshold value
    # Apply binary thresholding
    ret, binary_image = cv2.threshold(image, binary_threshold_value, 255, cv2.THRESH_BINARY)

    x1, y1, x2, y2 = predictions[0][0]

    roi = image[y1:y2, x1:x2]

    roi_bin = binary_image[y1:y2, x1:x2]
    black_pixels = np.sum(roi <= binary_threshold_value)
    total_pixels = roi.size
    percentage = float(black_pixels / total_pixels) * 100

    avg_intensity = roi.mean()
    avg_intensity_bin = roi_bin.mean()

    monitoring.logger_adapter.info(
        f"calculate_black_pixel_percentage average grayscale: {avg_intensity}      binary: {avg_intensity_bin}"
    )
    monitoring.logger_adapter.info(
        f"calculate_black_pixel_percentage black percentage grayscale with {binary_threshold_value} :"
        + f" {percentage}"
    )
    # show_image(binary_image)
    return percentage
