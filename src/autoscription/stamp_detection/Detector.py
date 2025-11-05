import os
from typing import Any, Dict, Optional, Tuple

import cv2
from numpy.typing import NDArray
from PIL.Image import Image
from stamp_processing import StampDetector

from src.autoscription.core.logging import Monitoring
from src.autoscription.core.utils import (
    crop_image,
    remove_line,
    remove_templates,
    rotate_image,
)

from .utils import calculate_black_pixel_percentage, remove_small_stamps


class Detector:
    stamp_detector: StampDetector
    config: Dict[str, Any]

    def __init__(self, config: Dict[str, Any], model_path: Optional[str] = None) -> None:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        self.stamp_detector = StampDetector(model_path=model_path, device="cpu")
        self.config = config

    def check_for_stamps(self, image_path: str, monitoring: Monitoring) -> Tuple[Image, NDArray, int]:
        opencv_image = cv2.imread(image_path, 0)
        color_converted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        remove_line(color_converted)
        remove_templates(
            color_converted=color_converted,
            template_paths=self.config["template_file_paths"],
            template_matching_threshold=self.config["template_matching_threshold"],
            color=self.config["color"],
            right_margin=self.config["right_margin"],
            left_margin=self.config["left_margin"],
            top_margin=self.config["top_margin"],
            bottom_margin=self.config["bottom_margin"],
            monitoring=monitoring,
        )
        image = crop_image(color_converted, self.config["horizontal_crop_point"], self.config["vertical_crop_point"])
        # show_image(image)
        predictions = self.stamp_detector([image])
        angle = 0
        original_image = image
        remove_small_stamps(predictions[0], image, self.config["area_ratio_threshold"])
        angle_list = [i if i % 10 == 0 else -i for i in range(0, self.config["max_rotation_angle"] + 1, 5)]
        if len(predictions[0]) == 0:
            for angle in angle_list:
                image = rotate_image(original_image, angle)
                predictions = self.stamp_detector([image])
                remove_small_stamps(predictions[0], original_image, self.config["area_ratio_threshold"])
                if len(predictions[0]) > 0:
                    break
        if len(predictions[0]) > 0:
            black_pixel_percentage = calculate_black_pixel_percentage(
                image, predictions, self.config["binary_threshold_value"], monitoring=monitoring
            )
            if black_pixel_percentage < self.config["black_pixel_percentage"]:
                predictions[0] = []
        return image, predictions[0], angle

    def count_stamps(self, file: str, expected_total: int, monitoring: Monitoring) -> Tuple[NDArray, int]:
        _, pr, angle = self.check_for_stamps(image_path=file, monitoring=monitoring)
        monitoring.logger_adapter.info(f"{len(pr)} stamps found out of {expected_total} at angle {angle}")
        return pr, angle
