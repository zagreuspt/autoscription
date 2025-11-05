from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from PIL.Image import Image
from pyzbar.pyzbar import Decoded, decode

from src.autoscription.core import utils
from src.autoscription.core.logging import Monitoring
from src.autoscription.core.utils import adjust_contrast_brightness
from src.autoscription.signature_detection.rectangle_utils import Point, Rect


def barcode_reader(file: str) -> List[Decoded]:
    """Returns unique CODE128 barcodes found in the image using different processing approaches."""
    img = cv2.imread(file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    all_barcodes = []

    def process_and_decode(image: np.ndarray) -> None:
        decoded = decode(image)
        for obj in decoded:
            # Decode only if it's CODE128 and data length is less than 16
            if obj.type == "CODE128" and len(obj.data.decode("utf-8")) < 16:
                # Add the decoded data (string) to the set for uniqueness
                all_barcodes.append(obj)

    process_and_decode(adjust_contrast_brightness(np.array(img), 1.9, -140))
    # Original grayscale
    process_and_decode(gray)

    # Enhanced with CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    process_and_decode(enhanced)

    # Blurred
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    del enhanced  # Free up memory

    # Binary threshold
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    process_and_decode(binary)

    # Adaptive thresholding variations
    for thresh_func in [
        lambda img: cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        lambda img: cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2),
        lambda img: cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2),
    ]:
        adaptive = thresh_func(blurred)  # type: ignore[no-untyped-call]
        process_and_decode(adaptive)
        process_and_decode(cv2.bitwise_and(binary, adaptive))
        del adaptive

    # Morphological operations
    kernel = np.ones((3, 3), np.uint8)
    morph_close = cv2.morphologyEx(
        cv2.bitwise_and(
            binary, cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        ),
        cv2.MORPH_CLOSE,
        kernel,
    )
    process_and_decode(morph_close)
    del morph_close

    # Adjusted contrast and brightness
    adjusted = cv2.convertScaleAbs(img, alpha=1.9, beta=-140)
    process_and_decode(adjusted)
    del adjusted, img, gray, blurred, binary  # Free up remaining memory

    unique_barcodes = []
    seen = set()
    for barcode in all_barcodes:
        barcode_data = barcode.data.decode("utf-8")
        if barcode_data not in seen:
            seen.add(barcode_data)
            unique_barcodes.append(barcode)

    return list(unique_barcodes)


def get_barcode_top_areas(barcodes: List[Decoded]) -> List[Dict[str, Any]]:
    return [
        {
            "type": barcode.type,
            "area": [
                barcode.rect.left,
                barcode.rect.top,
                barcode.rect.width if barcode.rect.width > 10 else 50,  # TODO: extract to configuration
                barcode.rect.height,
            ],
        }
        for barcode in barcodes
    ]


def get_barcode_bot_areas(barcodes: List[Decoded]) -> List[Dict[str, Any]]:
    """
    Get barcode from bottom areas.
    Height 1 is set because we need to correct the distance between
    the overlapping barcodes on the x axis.
    """
    return [
        {
            "type": barcode.type,
            "area": [barcode.rect.left, barcode.rect.top, barcode.rect.width if barcode.rect.width > 10 else 50, 50],
            # TODO: extract to configuration
        }
        for barcode in barcodes
    ]


def match_missing_coupons(config: Dict[str, Any], image: Image, monitoring: Monitoring) -> bool:
    total_templates_removed = utils.remove_templates(
        color_converted=image,
        template_paths=config["options"]["template_file_paths"],
        template_matching_threshold=config["options"]["template_matching_threshold"],
        monitoring=monitoring,
    )
    if total_templates_removed > 0:
        return True
    else:
        return False


def merge_bot_barcodes(bot_barcodes: List[Rect]) -> List[Rect]:
    more_overlaps = True
    while more_overlaps:
        overlaps = False
        for rect1 in bot_barcodes:
            for rect2 in bot_barcodes:
                if rect1 == rect2:
                    continue
                if rect1.overlaps_with(rect2):
                    l_x = min(rect1.l_top.x, rect2.l_top.x)
                    l_y = min(rect1.l_top.y, rect2.l_top.y)
                    l_point = Point(l_x, l_y)
                    width = int(max(l_point.distance_to_point(rect1.r_top), l_point.distance_to_point(rect2.r_top)))
                    bot_barcodes.append(Rect(rect1.name, [l_x, l_y, width, 50]))
                    bot_barcodes.remove(rect1)
                    bot_barcodes.remove(rect2)
                    overlaps = True
                    break
        if overlaps:
            break
        if not overlaps:
            more_overlaps = False
    return [Rect(rect.name, [rect.x, rect.y, rect.width, 2]) for rect in bot_barcodes]


# TODO: rename function
def count_coupons(barcodes: List[Decoded], monitoring: Monitoring) -> Tuple[List[Decoded], int]:
    # monitoring.logger_adapter.info('Count_coupons function started.')
    coupons_found = 0
    bot_barcodes = [
        Rect(f"bot{i + 1}", barcode["area"])
        for i, barcode in enumerate(get_barcode_bot_areas(barcodes))
        if barcode["type"] == "EAN13"
    ]
    bot_barcodes = merge_bot_barcodes(bot_barcodes)
    top_barcodes = [
        Rect(f"top{i + 1}", barcode["area"])
        for i, barcode in enumerate(get_barcode_top_areas(barcodes))
        if barcode["type"] == "CODE128"
    ]
    for barcode in top_barcodes + bot_barcodes:
        if barcode.width < 350:
            coupons_found += 1
        elif 350 < barcode.width < 900:
            coupons_found += 2
        elif 900 < barcode.width < 1350:
            coupons_found += 3
        else:
            coupons_found += 4
    for rect1 in bot_barcodes:
        for rect2 in top_barcodes:
            try:
                if rect1.overlaps_on_x_axis_with(rect2) and rect1.distance_to_rect(rect2, monitoring)["distance"] < 160:
                    coupons_found -= 1
            except Exception as e:  # TODO: root cause
                monitoring.logger_adapter.error("distance_to_rect failed")
                monitoring.logger_adapter.exception(e)
                continue
    monitoring.logger_adapter.info(f"{coupons_found} Coupons found")
    return barcodes, coupons_found


def get_authenticity_tapes(barcodes: List[Decoded]) -> str:
    return ",".join([barcode.data.decode("utf-8") for barcode in barcodes])
