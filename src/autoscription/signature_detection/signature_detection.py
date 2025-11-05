from __future__ import annotations

import gc
import math
from typing import Any

import cv2
import numpy as np
import torch
from numpy.typing import NDArray
from PIL import Image
from signature_detect.extractor import Extractor
from signature_detect.judger import Judger
from skimage import measure, morphology
from skimage.measure import regionprops

from src.autoscription.core.errors import RetriedException
from src.autoscription.core.logging import Monitoring
from src.autoscription.core.utils import (
    adjust_contrast_brightness,
    crop_segment,
    draw_bottom_right_templates,
    draw_signatures,
    remove_line,
    show_image,
)

from .craft import Craft
from .cropper import Cropper
from .loader import Loader


# TODO: extract magic numbers to config
def get_quartile_from_sensitivity(sensitivity: float) -> float:
    """
    Get the upper quartile based on sensitivity.
    Use sigmoid function for a smoother transition.
    """
    x = 10 - sensitivity
    if x <= 0:
        return 0
    elif x >= 10:
        return 1
    else:
        x -= 2
        return 1 / (1 + math.exp(-x))


class SignatureDetector:
    craft: Craft
    monitoring: Monitoring
    loader: Loader
    extractor: Extractor
    judger: Judger
    configuration: dict[str, Any]
    is_debug_enabled: bool

    def __init__(self, monitoring: Monitoring, configuration: dict[str, Any], is_debug_enabled: bool = False) -> None:
        try:
            self.craft = Craft(configuration["weight_directory"])
        except Exception as e:
            monitoring.logger_adapter.exception(e)
            monitoring.logger_adapter.warning("Craft instantiation failed... Retrying")
            torch.cuda.empty_cache()
            torch.set_grad_enabled(False)
            self.craft = Craft(configuration["weight_directory"])
        self.is_debug_enabled = is_debug_enabled
        self.configuration = configuration
        cropper_config = configuration["options"]["preprocessing"]["cropper"]
        self.loader = Loader(low_threshold=(0, 0, 210), high_threshold=(255, 255, 255))  # TODO: extract to config
        self.cropper = Cropper(
            min_region_size=cropper_config["min_region_size"],
            border_ratio=0,  # TODO: Extract to config
            increase_box_margin=cropper_config["increase_box_margin"],
            clean_y_axis=cropper_config["clean_y_axis"],
        )
        self.extractor = Extractor(amplfier=100, min_area_size=10, outlier_weight=3, outlier_bias=100)
        self.judger = Judger()
        self.monitoring = monitoring

    def detect_text(self, image: Image) -> dict[str, Any]:
        try:
            return dict(self.craft.detect_text(image))
        except Exception as e:
            self.monitoring.logger_adapter.exception(RetriedException(e))
            self.monitoring.logger_adapter.warning("Text detection failed... Retrying")
            torch.cuda.empty_cache()
            torch.set_grad_enabled(False)
            gc.collect()
            return dict(self.craft.detect_text(image))

    def remove_texts_from_img(self, img: Image) -> Image:
        img_edit = img.copy()
        prediction_result = self.detect_text(img_edit)
        boxes = prediction_result["boxes"]
        for box in boxes:
            # Create a mask of the same size as the original image
            mask = np.zeros_like(img_edit)
            # Fill the bounding box with white color
            cv2.fillPoly(mask, np.int32([box]), (255, 255, 255))
            # Fill the bounding box with white color
            cv2.fillPoly(img_edit, np.int32([box]), (255, 255, 255))
        return img_edit

    def get_area_signatures(
        self, img_area: str, min_check_area: float, min_height: int, debug_signature_area: bool
    ) -> list[NDArray]:
        mask = self.loader.get_masks(img_area)[0]
        results = [result for _, result in self.cropper.run(mask).items()]
        judger_results = [
            signature
            for signature in results
            if self.judger.judge(signature["cropped_mask"]) and signature["cropped_region"][-1] > min_height
        ]
        if self.is_debug_enabled and debug_signature_area:
            self.monitoring.logger_adapter.info("Cropper Results:")
            draw_signatures(
                img_area,
                [{"cropped_region": result["cropped_region"]} for result in results],
                monitoring=self.monitoring,
            )
            show_image(img_area)
        if min_check_area < sum(
            [result["cropped_region"][-1] * result["cropped_region"][-2] for result in judger_results]
        ):
            return judger_results
        return []

    def count_signatures(
        self,
        file: str,  # noqa: C901
        horizontal_crop_points: list[tuple[int, int]],
        detectors_preprocessing_config: dict[str, Any],  # TODO: pass it during SignatureDetector instantiation
        min_right_area: int = 15000,
    ) -> tuple[list[NDArray], int]:
        vertical_crop_point: float = self.configuration["options"]["doc_vertical_crop_point"]
        preprocessing_config: dict[str, Any] = self.configuration["options"]["preprocessing"]
        min_height: int = self.configuration["options"]["min_box_height"]
        min_area: int = self.configuration["options"]["min_area"]

        img = Image.open(file)
        img_array = np.array(img)
        rgb_img = Image.fromarray(img_array).convert("RGB")
        org_img = adjust_contrast_brightness(np.array(rgb_img), 1.9, -140)

        img_arr = org_img.copy()

        if preprocessing_config["remove_line"]:
            remove_line(img_arr)
            if self.is_debug_enabled:
                self.monitoring.logger_adapter.info("Document after line removal")
                show_image(img_arr)
        draw_bottom_right_templates(
            img=img_arr,
            detectors_preprocessing_config=detectors_preprocessing_config,
            color=(255, 255, 255),
            monitoring=self.monitoring,
        )
        if self.is_debug_enabled:
            self.monitoring.logger_adapter.info("File after draw_bottom_right_templates function:")
            show_image(img_arr)

        extract_sign_config = preprocessing_config["extract_signatures"]

        if extract_sign_config["is_enabled"]:
            img_arr = self.extract_signatures(
                img=img_arr,
                sensitivity=extract_sign_config["options"]["primary_extractor_sensitivity"],
            )
            if self.is_debug_enabled:
                self.monitoring.logger_adapter.info("Document after primary signature extraction.")
                show_image(img_arr)

        img_arr = crop_segment(img_arr, vertical_crop_point)
        if self.is_debug_enabled:
            self.monitoring.logger_adapter.info("File after crop_segment")
            show_image(img_arr)

        remove_text_config = preprocessing_config["remove_texts"]
        if remove_text_config["is_enabled"] and remove_text_config["options"]["run_in_whole_doc"]:
            try:
                img_arr = self.remove_texts_from_img(img_arr)
                if self.is_debug_enabled:
                    self.monitoring.logger_adapter.info("Document after text removal")
                    show_image(img_arr)
                min_right_area = remove_text_config["options"]["min_right_area"]
            except Exception as e:
                self.monitoring.logger_adapter.exception(e)
                self.monitoring.logger_adapter.warning("Text detector failed for this image")

        signatures = []
        signature_count = 0
        area_length = len(horizontal_crop_points)
        secondary_extractor_print = False
        for area, (start, end) in enumerate(horizontal_crop_points):
            right_area = area == area_length - 1
            if right_area:
                min_check_area = min_right_area
            else:
                min_check_area = min_area
            try:
                cut_image = crop_segment(img_arr.copy(), vertical_crop_point, start, end)
            except Exception as e:
                self.monitoring.logger_adapter.warning("Failed to cut image - Retrying ...")
                self.monitoring.logger_adapter.exception(RetriedException(e))
                gc.collect()
                cut_image = crop_segment(img_arr.copy(), vertical_crop_point, start, end)

            if (
                remove_text_config["is_enabled"]
                and right_area
                and remove_text_config["options"]["run_in_stamp_area"]
                and (not remove_text_config["options"]["run_in_whole_doc"])
            ):
                try:
                    cut_image = self.remove_texts_from_img(cut_image)
                    if self.is_debug_enabled:
                        self.monitoring.logger_adapter.info("After text removal")
                        show_image(cut_image)
                    min_check_area = remove_text_config["options"]["min_right_area"]
                except Exception as e:
                    self.monitoring.logger_adapter.exception(e)
                    self.monitoring.logger_adapter.warning("Text detector failed for this image")

            # Get the judged signatures of the area
            judged_signatures = self.get_area_signatures(
                cut_image,
                min_check_area,
                min_height,
                preprocessing_config["extract_signatures"]["debug"],
            )

            # If no signatures, try again with secondary extractor
            if (
                (not judged_signatures)
                and (not right_area)
                and extract_sign_config["is_enabled"]
                and extract_sign_config["options"]["secondary_extractor"]
            ):
                sec_ext_img = org_img.copy()
                if preprocessing_config["remove_line"]:
                    remove_line(sec_ext_img)
                img_arr_sec = self.extract_signatures(
                    img=sec_ext_img,
                    sensitivity=extract_sign_config["options"]["secondary_extractor_sensitivity"],
                )
                try:
                    cut_image_sec = crop_segment(img_arr_sec.copy(), vertical_crop_point, start, end)
                except Exception as e:
                    self.monitoring.logger_adapter.warning("Failed to cut image - Retrying ...")
                    self.monitoring.logger_adapter.exception(RetriedException(e))
                    gc.collect()
                    cut_image_sec = crop_segment(img_arr_sec.copy(), vertical_crop_point, start, end)
                if not secondary_extractor_print:
                    self.monitoring.logger_adapter.info("Secondary extraction run successfully")
                    if self.is_debug_enabled:
                        self.monitoring.logger_adapter.info(
                            "After secondary extraction " + "(to be used for missing signatures only)"
                        )
                        show_image(cut_image_sec)
                    secondary_extractor_print = True
                judged_signatures = self.get_area_signatures(
                    cut_image_sec,
                    min_check_area,
                    min_height,
                    preprocessing_config["extract_signatures"]["debug"],
                )

            signatures += judged_signatures
            signature_count += 1 if judged_signatures else 0

            self.monitoring.logger_adapter.info(f"{signature_count} signatures found.")
        return signatures, signature_count

    def extract_signatures(self, img: Image, sensitivity: float = 3.6) -> NDArray:
        debug = self.configuration["options"]["preprocessing"]["extract_signatures"]["debug"]
        if self.is_debug_enabled and debug:
            self.monitoring.logger_adapter.info(f"extract_signatures started with sensitivity: {sensitivity}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]  # ensure binary
        if self.is_debug_enabled and debug:
            self.monitoring.logger_adapter.info(
                "image altered to binary with 127 threshold value"
                + "( If a pixel value is greater than or equal to this value, "
                + "it will be set to the maximum value (255); "
                + "otherwise, it will be set to 0.)"
            )
        # connected component analysis by scikit-learn framework
        blobs = img > img.mean()
        self.monitoring.logger_adapter.info(f"The extractor img.mean() is : {img.mean()}")
        blobs_labels = measure.label(blobs, background=1)
        regions = regionprops(blobs_labels)
        areas = [r.area for r in regions if r.area > 10]

        counter = len(areas)
        total_area = sum(areas)
        average = total_area / counter

        # calculate constants based on sensitivity
        low_quartile = get_quartile_from_sensitivity(sensitivity)

        quartiles = [low_quartile, 1]
        low_thres_index = max(int(quartiles[0] * len(areas)) - 1, 0)
        high_thres_index = max(int(quartiles[1] * len(areas)) - 1, 0)
        if self.is_debug_enabled and debug:
            self.monitoring.logger_adapter.info(f"counter ={counter}")
            self.monitoring.logger_adapter.info(f"total_area ={total_area}")
            self.monitoring.logger_adapter.info(f"average ={average}")
            self.monitoring.logger_adapter.info(f"low_quartile ={low_quartile}")

        # a4_small_size_outliar_constant is used as a threshold value to
        # remove connected outliar connected pixels
        # are smaller than a4_small_size_outliar_constant for A4 size
        # scanned documents
        a4_small_size_outliar_constant = sorted(areas)[low_thres_index]
        # a4_big_size_outliar_constant is used as a threshold value to remove
        # outliar connected pixels are bigger than a4_big_size_outliar_constant
        # for A4 size scanned documents
        a4_big_size_outliar_constant = sorted(areas)[high_thres_index]

        # remove the connected pixels are smaller than a4_small_size_
        # outliar_constant
        try:
            pre_version = morphology.remove_small_objects(blobs_labels, a4_small_size_outliar_constant)
        except Exception as e:
            self.monitoring.logger_adapter.warning("remove_small_objects failed - Retrying...")
            self.monitoring.logger_adapter.exception(RetriedException(e))
            gc.collect()
            pre_version = morphology.remove_small_objects(blobs_labels, a4_small_size_outliar_constant)
        # remove the connected pixels are bigger than threshold a4_big_size
        # _outliar_constant
        # to get rid of undesired connected pixels such as table headers and etc.
        component_sizes = np.bincount(pre_version.ravel())
        too_small = component_sizes > (a4_big_size_outliar_constant)
        too_small_mask = too_small[pre_version]
        pre_version[too_small_mask] = 0

        # ensure binary
        img = cv2.convertScaleAbs(pre_version)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        if self.is_debug_enabled and debug:
            self.monitoring.logger_adapter.info("final image output from extract_signatures function")
            show_image(img)
        return np.stack((img,) * 3, axis=-1)
