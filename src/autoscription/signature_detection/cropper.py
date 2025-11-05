from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image


class Cropper:
    """
    read the mask extracted by Extractor, and crop it.
    Attributes:
    -----------
      - min_region_size
        the min area size of the signature.
      - border_ratio: float
          border = min(h, w) * border_ratio
          h, w are the heigth and width of the input mask.
          The border will be removed by the function _remove_borders.
    Methods:
    --------
      - find_contours(img: numpy array) -> sorted_boxes: numpy array
        find the contours and sort them by area size
      - is_intersected(box_a: [x, y, w, h], box_b: [x, y, w, h]) -> bool
        check box_a and box_b is intersected
      - merge_boxes(box_a: [x, y, w, h], box_b: [x, y, w, h]) -> [x, y, w, h]:
        merge the intersected boxes into one
      - boxes2regions(sorted_boxes) -> dict:
        transform all the sorted_boxes into regions (merged boxes)
      - crop_regions(img: numpy array, regions: dict) -> list:
        return a list of cropped images (np.array)
      - run(img_path) -> list
        main function, crop the signatures,
        return a list of cropped images (np.array)
    """

    def __init__(
        self,
        min_region_size: int = 10000,
        border_ratio: float = 0.1,
        increase_box_margin: int = 0,
        clean_y_axis: bool = True,
    ) -> None:
        self.min_region_size = min_region_size
        self.border_ratio = border_ratio
        self.increase_box_margin = increase_box_margin
        self.clean_y_axis = clean_y_axis

    def __str__(self) -> str:
        s = "\nCropper\n==========\n"
        s += f"min_region_size = {self.min_region_size}\n"
        s += f"border_ratio = {self.border_ratio}\n"
        return s

    def find_contours(self, img: Image) -> NDArray:
        """
        Find contours limited by min_region_size in the binary image.
        The contours are sorted by area size, from large to small.
        Params:
          img: numpy array
        Return:
          boxes: A numpy array of contours.
          each items in the array is a contour (x, y, w, h)
        """
        cnts = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = cnts[0] if len(cnts) == 2 else cnts[1]
        boxes = []
        copy_img = img.copy()
        for c in cnt:
            (x, y, w, h) = cv2.boundingRect(c)

            if self.min_region_size < h * w < 100000 and h < copy_img.shape[0] and w < copy_img.shape[1] and h > 30:
                boxes.append(
                    [
                        x - self.increase_box_margin,
                        y - self.increase_box_margin,
                        w + self.increase_box_margin,
                        h + self.increase_box_margin,
                    ]
                )

        np_boxes: NDArray = np.array(boxes)
        # sort the boxes by area size
        area_size: list[int] = list(map(self.__calculate_area, np_boxes))
        area_size_array: NDArray = np.array(area_size)
        area_dec_order = area_size_array.argsort()[::-1]
        sorted_boxes = np_boxes[area_dec_order]

        return sorted_boxes

    def is_intersected(self, new_box: list[int], orignal_box: list[int]) -> bool:
        [x_a, y_a, w_a, h_a] = new_box
        [x_b, y_b, w_b, h_b] = orignal_box

        if y_a > y_b + h_b:
            return False
        if y_a + h_a < y_b:
            return False
        if x_a > x_b + w_b:
            return False
        if x_a + w_a < x_b:
            return False
        return True

    def merge_boxes(self, box_a: list[int], box_b: list[int]) -> list[int]:
        """Merge 2 intersected box into one."""
        [x_a, y_a, w_a, h_a] = box_a
        [x_b, y_b, w_b, h_b] = box_b

        min_x = min(x_a, x_b)
        min_y = min(y_a, y_b)
        max_w = max(w_a, w_b, (x_b + w_b - x_a), (x_a + w_a - x_b))
        max_h = max(h_a, h_b, (y_b + h_b - y_a), (y_a + h_a - y_b))

        return [min_x, min_y, max_w, max_h]

    def _remove_borders(self, box: list[int]) -> list[int]:
        """Remove the borders around the box."""
        [x, y, w, h] = box
        border = math.floor(min(w, h) * self.border_ratio)
        return [x + border, y + border, w - border, h - border]

    def boxes2regions(self, sorted_boxes: list[list[int]]) -> dict[str, list[int]]:
        regions: dict[str, list[int]] = {}

        for box in sorted_boxes:
            if len(regions) == 0:
                regions["0"] = box
            else:
                is_merged = False
                key: str
                region: NDArray
                for key, region in regions.items():
                    if self.is_intersected(box, region):
                        new_region = self.merge_boxes(region, box)
                        regions[key] = self._remove_borders(new_region)
                        is_merged = True
                        break
                if not is_merged:
                    key = len(regions).__str__()
                    regions[key] = self._remove_borders(box)

        return regions

    def get_cropped_masks(self, mask: NDArray, regions: dict[str, NDArray]) -> dict[str, NDArray]:
        """Return cropped masks."""
        results = {}
        for key, region in regions.items():
            [x, y, w, h] = region
            image = Image.fromarray(mask)
            cropped_image = image.crop((x, y, x + w, y + h))
            cropped_mask = np.array(cropped_image)

            results[key] = cropped_mask
        return results

    def merge_regions_and_masks(self, mask: NDArray, regions: dict[str, NDArray]) -> dict[str, Any]:
        """Helper function: put regions and masks in a dict, and return it."""
        cropped_image = self.get_cropped_masks(mask, regions)
        results = {}

        for key in regions.keys():
            results[key] = {
                "cropped_region": regions[key],
                "cropped_mask": cropped_image[key],
            }

        return results

    def run(self, np_image: NDArray) -> dict[str, NDArray]:
        """Read the signature extracted by Extractor, and crop it."""
        # find contours
        sorted_boxes = self.find_contours(np_image)

        # get regions
        regions = self.boxes2regions(sorted_boxes)

        # crop regions
        results = self.merge_regions_and_masks(np_image, regions)

        if self.clean_y_axis:
            boxes = []
            whitelist_boxes = {}
            cnt = 0
            for cropped_id, cropped in results.items():
                boxes.append({"id": cropped_id, "values": cropped["cropped_region"]})

            while boxes:
                whitelist_boxes[cnt] = boxes[0]
                del boxes[0]
                remove_items = []
                for box in boxes:
                    [x_a, _, w_a, h_a] = whitelist_boxes[cnt]["values"]
                    [x_b, _, w_b, h_b] = box["values"]
                    if (
                        x_a <= x_b <= x_a + w_a
                        or x_a <= x_b + w_b <= x_a + w_a
                        or x_b <= x_a <= x_b + w_b
                        or x_b <= x_a + w_a <= x_b + w_b
                    ):
                        if w_b * h_b > w_a * h_a:
                            whitelist_boxes[cnt] = box
                        remove_items.append(box)
                for item in remove_items:
                    boxes.remove(item)
                cnt += 1

            results = {
                key: value for key, value in results.items() if key in [box["id"] for box in whitelist_boxes.values()]
            }
        image = Image.fromarray(np_image)
        for _, result in results.items():
            [x, y, w, h] = result["cropped_region"]
            extra_margin = 50
            cropped_image = image.crop((x - extra_margin, y - extra_margin, x + w + extra_margin, y + h + extra_margin))
            result["cropped_mask"] = np.array(cropped_image)

        return results

    def __calculate_area(self, box: list[int]) -> int:
        return box[2] * box[3]
