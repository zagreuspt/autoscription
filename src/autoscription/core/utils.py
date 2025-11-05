import gc
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from easyocr import Reader
from IPython.core.display_functions import clear_output
from numpy.typing import NDArray
from PIL import Image
from pyzbar.pyzbar import Decoded

from src.autoscription.core.errors import RetriedException
from src.autoscription.core.logging import Monitoring
from src.autoscription.signature_detection.rectangle_utils import (
    Rect,
    min_rectangles_distances,
)


def generate_past_partial_executions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    # Step 1: Filter the DataFrame to include only those rows where 'execution' is greater than 1
    df["execution"] = df["execution"].astype(int)
    # Step 2: Group by 'prescription' and find the minimum 'execution' for each group
    filtered_df = df.groupby("prescription")["execution"].min().reset_index()
    filtered_df = filtered_df[filtered_df["execution"] > 1]

    # Step 3: Convert the filtered DataFrame into a list of tuples containing 'prescription' and 'execution'
    current_day_last_exec = filtered_df[["prescription", "execution"]].to_records(index=False).tolist()

    max_execution = {prescription: execution for prescription, execution in current_day_last_exec}
    # Step 4: Generate tuples for each prescription
    result = []
    for prescription, max_exec in max_execution.items():
        for exec in range(1, max_exec):
            result.append({"prescription": prescription, "execution": exec})
    return result


def mark_predictions(image: Image, predictions: List[List[int]]) -> None:
    for box in predictions:
        cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 128, 0), 5)


def rotate_image(img_arr: NDArray, rotation: int) -> NDArray:
    img = Image.fromarray(img_arr)
    img = img.rotate(rotation, Image.NEAREST, expand=True, fillcolor=(255, 255, 255))
    return np.array(img)


def crop_image(opencv_image: Image, horizontal_crop_point: float, vertical_crop_point: float) -> Image:
    # monitoring.logger_adapter.info('utils.crop_image function was called and is about to run')
    img_arr = opencv_image
    img_arr[0 : int(len(img_arr) * vertical_crop_point), 0:] = (255, 255, 255)
    img_arr[0:, 0 : int(len(img_arr[0]) * horizontal_crop_point)] = (255, 255, 255)
    return img_arr


def crop_and_convert_rotate_image(
    opencv_image: Image, rotation: int, horizontal_crop_point: float, vertical_crop_point: float
) -> Image:
    img_arr = crop_image(opencv_image, horizontal_crop_point, vertical_crop_point)
    return rotate_image(img_arr, rotation)


def blank_page_removal(dataset_path: Path, monitoring: Monitoring) -> None:
    files = list(dataset_path.glob("*.jpg"))
    threshold = 254
    for _, file in enumerate(files):
        img = cv2.imread(str(file), cv2.IMREAD_GRAYSCALE)  # read the image as grayscale directly
        if img is not None:
            _, img_adj = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
            avg = np.average(img_adj)
            if avg > threshold:
                os.remove(str(file))  # delete the file
                monitoring.logger_adapter.warning(
                    f"{file} was deleted as a blank page with an Average Pixel Density of {avg}"
                )
        else:
            monitoring.logger_adapter.warning(f"Could not read image: {file}")


def show_image(img: Image) -> None:
    _, image = plt.subplots(figsize=(40, 20))
    image.imshow(img)
    image.set_axis_off()
    plt.tight_layout()
    plt.show()


def crop_segment(
    img_arr: NDArray,
    vertical_crop_point: float = 0.9,
    horizontal_crop_start: float = 0.3,
    horizontal_crop_end: float = 1.0,
) -> NDArray:
    """Crops the image."""
    # Opening the image and converting
    # it to RGB color mode
    # IMAGE_PATH => Path to the image
    # Extracting the image data &
    # creating an numpy array out of it
    # Turning the pixel values of the 400x400 pixels to black
    img_arr[0 : int(len(img_arr) * vertical_crop_point), 0:] = (255, 255, 255)
    img_arr[0:, 0 : int(len(img_arr[0]) * 0.30)] = (255, 255, 255)
    img_arr[0:, 0 : int(len(img_arr[0]) * horizontal_crop_start)] = (255, 255, 255)
    img_arr[0:, int(len(img_arr[0]) * horizontal_crop_end) : int(len(img_arr[0]) * 1)] = (255, 255, 255)
    return img_arr


def remove_line(src: Image) -> Image:
    """Removes horizontal lines."""
    # Transform source image to gray if it is not already
    if len(src.shape) != 1:
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    else:
        gray = src

    # Apply adaptive threshold to the negative of the gray image to
    # extract black lines
    gray = cv2.bitwise_not(gray)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 19, -2)

    # Create the images that will use to extract the horizontal
    # and vertical lines
    horizontal = np.copy(bw)
    vertical = np.copy(bw)

    # Specify size on horizontal axis
    cols = horizontal.shape[1]
    horizontal_size = cols // 30

    # Create structure element for extracting horizontal lines through
    # morphology operations
    horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 4))

    # Apply morphology operations to extract horizontal lines
    horizontal = cv2.erode(horizontal, horizontal_structure)
    horizontal = cv2.dilate(horizontal, horizontal_structure)
    # show_image(horizontal)

    # Specify size on vertical axis
    rows = vertical.shape[0]
    verticalsize = rows // 30

    # Create structure element for extracting vertical lines through
    # morphology operations
    vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))

    # Apply morphology operations to extract vertical lines
    vertical = cv2.erode(vertical, vertical_structure)
    vertical = cv2.dilate(vertical, vertical_structure)

    # Find contours of horizontal lines and draw them on the source image
    cnts = cv2.findContours(horizontal, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(src, [c], -1, (255, 255, 255), 5)

    # Find contours of vertical lines and draw them on the source image
    cnts = cv2.findContours(vertical, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(src, [c], -1, (255, 255, 255), 4)
    # if is_debug_enabled:
    # show_image(src)
    # Return the modified image with the lines removed

    # monitoring.logger_adapter.info('Line removal run successfully.')
    return src


def remove_text(image: Image) -> Image:
    """Removes text from image."""
    g_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Otsu Thresholding
    blur = cv2.GaussianBlur(g_image, (1, 1), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    new_contours = []
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        if h > 36:
            continue
        new_contours.append(contour)
    #     cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 3)
    # return image
    img = cv2.drawContours(image, new_contours, -1, (255, 255, 255), 2)
    # img = image
    return img


def remove_template(
    image: Image,
    template: Image,
    template_matching_threshold: float,
    monitoring: Monitoring,
    color: Tuple[int, int, int] = (255, 255, 255),
    right_margin: int = 0,
    left_margin: int = 0,
    top_margin: int = 0,  # New parameter for the vertical margin
    bottom_margin: int = 0,  # Additional parameter for controlling bottom margin if needed
) -> Tuple[int, int, int]:
    total_points = 0
    w, h = template.shape[::-1]
    try:
        res = cv2.matchTemplate(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), template, cv2.TM_CCOEFF_NORMED)
    except Exception as e:
        monitoring.logger_adapter.exception(RetriedException(e))
        monitoring.logger_adapter.error("Failed during remove_template, Retrying...")
        gc.collect()
        res = cv2.matchTemplate(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), template, cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    loc = np.where(res >= template_matching_threshold)
    points = zip(*loc[::-1])

    for point in points:
        top_left = (point[0] - left_margin, point[1] - top_margin)  # Adjusting for top margin
        bottom_right = (point[0] + w + right_margin, point[1] + h + bottom_margin)  # Adjusting for bottom margin
        cv2.rectangle(image, top_left, bottom_right, color, -1)
        # cv2.putText(image, f'{template_name}', top_left,
        # cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 2, cv2.LINE_AA)
        total_points = total_points + 1
    return total_points, max_loc, max_val


def remove_templates(
    color_converted: Image,
    monitoring: Monitoring,
    template_paths: List[str],
    template_matching_threshold: float,
    color: Tuple[int, int, int] = (255, 255, 255),
    right_margin: int = 0,
    left_margin: int = 0,
    top_margin: int = 0,
    bottom_margin: int = 0,
) -> int:
    points = 0
    for template_path in template_paths:
        template_name = Path(template_path).name
        template = cv2.imread(template_path)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        try:
            points, max_loc, max_val = remove_template(
                image=color_converted,
                template=gray_template,
                template_matching_threshold=template_matching_threshold,
                monitoring=monitoring,
                color=color,
                right_margin=right_margin,
                left_margin=left_margin,
                top_margin=top_margin,
                bottom_margin=bottom_margin,
            )
        except Exception as e:
            monitoring.error("Failed during remove_templates, Retrying...")
            monitoring.exception(RetriedException(e))
            gc.collect()
            points, max_loc, max_val = remove_template(
                image=color_converted,
                template=gray_template,
                template_matching_threshold=template_matching_threshold,
                monitoring=monitoring,
                color=color,
                right_margin=right_margin,
                left_margin=left_margin,
                top_margin=top_margin,
                bottom_margin=bottom_margin,
            )
        if points > 0:
            monitoring.logger_adapter.info(
                f"Found {points} points with a match {template_name} "
                f"at loc:({max_loc}) and correlation of {max_val})"
            )
            break
    return points


def draw_barcodes(img: Image, barcodes: List[Decoded], monitoring: Monitoring) -> None:
    box_number = 1
    rectangles = []
    for barcode in barcodes:
        [x, y, w, h] = barcode.rect
        rectangles.append(Rect(str(box_number), [x, y, w, h]))
        cv2.rectangle(img, (x, y), (x + w, y + h), (155, 50, 0), 5)
        cv2.putText(img, f"{box_number}", (x + int(w / 2) - 5, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (155, 50, 0), 6)
        monitoring.logger_adapter.info(f'Barcode {barcode.data.decode("utf-8")} {box_number}: ' f"{w} x {h} = {w * h}")
        box_number += 1


def draw_stamps(img: Image, pr: List[List[int]], angle: int) -> Image:
    rotated_image = rotate_image(img, angle)
    mark_predictions(rotated_image, pr)
    rotated_image_a = rotate_image(rotated_image, (-1 * angle))
    # cv2.putText(rotated_image_a, f'{angle}', (200, 200),
    # cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 0, 0), 6)
    return rotated_image_a


def draw_signatures(img: Image, signatures: List[Dict[str, List[int]]], monitoring: Monitoring) -> None:
    box_number = 1
    rectangles = []
    for cropped in signatures:
        [x, y, w, h] = cropped["cropped_region"]
        rectangles.append(Rect(str(box_number), [x, y, w, h]))
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 5)
        cv2.putText(img, f"{box_number}", (x + int(w / 2) - 5, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 50, 0), 6)
        monitoring.logger_adapter.info(f"Signature {box_number}: {w} x {h} = {w * h}")
        box_number += 1
    monitoring.logger_adapter.info(f"{len(signatures)} signatures found (draw_signatures function)")
    try:
        monitoring.logger_adapter.info("\n".join(list(set(min_rectangles_distances(rectangles, monitoring)))))
    except Exception as e:
        monitoring.logger_adapter.error(e)


def draw_signature_areas(
    img: Image, vertical_crop_point: float, horizontal_crop_points: List[Tuple[float, float]]
) -> None:
    height, width, _ = img.shape
    for horizontal_crop_point in horizontal_crop_points:
        cv2.rectangle(
            img,
            (int(horizontal_crop_point[0] * width), int(vertical_crop_point * height)),
            (int(horizontal_crop_point[1] * width), height),
            (153, 50, 204),
            5,
        )


def draw_bottom_right_templates(
    img: Image,
    detectors_preprocessing_config: Dict[str, Any],
    monitoring: Monitoring,
    color: Tuple[int, int, int] = (255, 255, 255),
) -> None:
    if detectors_preprocessing_config["is_enabled"]:
        options = detectors_preprocessing_config["options"]
        remove_templates(
            color_converted=img,
            template_paths=options["template_file_paths"],
            template_matching_threshold=options["template_matching_threshold"],
            color=color,
            right_margin=options["right_margin"],
            left_margin=options["left_margin"],
            top_margin=options["top_margin"],
            bottom_margin=options["bottom_margin"],
            monitoring=monitoring,
        )


def get_barcode_ocr(reader: Reader, file: Path, monitoring: Monitoring) -> Tuple[str, str]:
    # Open the image file
    image = Image.open(file)
    # Set the crop coordinates (left, top, right, bottom)
    crop_coords = (750, 100, 1400, 550)
    crop_coords_2 = (1400, 150, 2480, 650)
    # Crop the image
    cropped_image = image.crop(crop_coords)
    cropped_image_2 = image.crop(crop_coords_2)
    digit_chunks = reader.readtext(image=np.array(cropped_image), allowlist="0123456789", detail=0)
    digit_chunks_2 = reader.readtext(image=np.array(cropped_image_2), allowlist="0123456789", detail=0)
    monitoring.logger_adapter.info(f"OCR (crop1): {digit_chunks}")
    monitoring.logger_adapter.info(f"OCR (crop2):{digit_chunks_2}")

    empty_barcode = str(0).zfill(16)

    barcode = __get_valid_barcode(digit_chunks, monitoring)
    barcode_2 = __get_valid_barcode(digit_chunks_2, monitoring)
    if barcode and barcode_2:
        barcode = barcode.strip()
        barcode_2 = barcode_2.strip()
        if barcode == barcode_2:
            monitoring.logger_adapter.warning(f"File: {file} | OCR barcodes match: {barcode} == {barcode_2}")
            return barcode, ""
        else:
            monitoring.logger_adapter.warning(f"File: {file} | OCR barcodes do not match: {barcode} != {barcode_2}")
            return empty_barcode, f"{barcode}|{barcode_2}"
    else:
        monitoring.logger_adapter.warning(f"File: {file} | OCR barcodes not found")
        return empty_barcode, ""


def __get_valid_barcode(digit_chunks: List[str], monitoring: Monitoring) -> Optional[str]:
    barcode: Optional[str] = None
    for i, digits in enumerate(digit_chunks):
        if __start_with_valid_date(digits):
            if len(digits) == 13:
                if i + 1 < len(digit_chunks):  # checking if the next index exists
                    potential_barcode = digits + digit_chunks[i + 1]
                    if len(potential_barcode) == 16:
                        barcode = digits + digit_chunks[i + 1]
                    break
                else:
                    monitoring.logger_adapter.warning(
                        "Next index doesn't exist, can't form barcode"
                    )  # TODO: replace with metrics counter

            elif len(digits) == 16:
                barcode = digits
                break
        # else:
        # monitoring.logger_adapter.warning("Potential barcode does not start with valid date")
    return barcode


def __start_with_valid_date(potential_barcode: str) -> bool:
    potential_date = potential_barcode[:6]
    try:
        date_from_digits = datetime.strptime(potential_date, "%y%m%d")
        return datetime.today().year >= date_from_digits.year > 2020
    except ValueError:
        return False


def rotate_image_180(image: Image) -> Image:
    # Rotate the image by 180 degrees
    rotated_img = image.rotate(180)
    return rotated_img


def ipython_clear_output() -> None:
    if not hasattr(sys, "_MEIPASS"):
        clear_output(wait=True)


def adjust_contrast_brightness(img: Image, contrast: float = 1.0, brightness: int = 0) -> Image:
    """
    Adjusts contrast and brightness of an uint8 image.
    contrast:   (0.0,  inf) with 1.0 leaving the contrast as is
    brightness: [-255, 255] with 0 leaving the brightness as is
    """
    brightness += int(round(255 * (1 - contrast) / 2))
    return cv2.addWeighted(img, contrast, img, 0, brightness)
