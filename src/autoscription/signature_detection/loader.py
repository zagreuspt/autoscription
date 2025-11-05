from typing import List, Tuple

import cv2
from numpy.typing import NDArray


class Loader:
    """
    Load an image or a pdf file.

    Attributes
    ----------
    low_threshold: tuple
        The low threshold of cv2.inRange
    high_threshold: tuple
        The high threshold of cv2.inRange

    Methods
    -------
    get_masks(path: str) -> list
        It read an image or a pdf file page by page.
        It returns the masks that the bright parts are marked as 255,
        the rest as 0.
    """

    def __init__(
        self, low_threshold: Tuple[int, int, int] = (0, 0, 250), high_threshold: Tuple[int, int, int] = (255, 255, 255)
    ) -> None:
        if self._is_valid(low_threshold):
            self.low_threshold = low_threshold
        if self._is_valid(high_threshold):
            self.high_threshold = high_threshold

    def __str__(self) -> str:
        s = "\nLoader\n==========\n"
        s += f"low_threshold = {self.low_threshold}\n"
        s += f"high_threshold = {self.high_threshold}\n"
        return s

    def _is_valid(self, threshold: Tuple[int, int, int]) -> bool:
        if type(threshold) is not tuple:
            raise Exception("The threshold must be a tuple.")
        if len(threshold) != 3:
            raise Exception("The threshold must have 3 item (h, s, v).")
        for item in threshold:
            if item not in range(0, 256):
                raise Exception("The threshold item must be in the range [0, 255].")
        return True

    def get_masks(self, path: str) -> List[NDArray]:
        # basename = os.path.basename(path)
        # dn, dext = os.path.splitext(basename)
        # ext = dext[1:].lower()
        # if ext == "pdf":
        #     self.document_type = "PDF"
        # elif ext == "jpg" or ext == "jpeg" or ext == "png" or ext == "tif":
        #     self.document_type = "IMAGE"
        # else:
        #     raise Exception("Document should be jpg/jpeg, png, tif or pdf.")

        # if self.document_type == "IMAGE":
        loader = _ImageWorker(self.low_threshold, self.high_threshold)
        return [loader.get_image_mask(path)]

        # if self.document_type == "PDF":
        #     loader = _PdfWorker(self.low_threshold, self.high_threshold)
        #     return loader.get_pdf_masks(path)


class _ImageWorker:
    def __init__(self, low_threshold: Tuple[int, int, int], high_threshold: Tuple[int, int, int]) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def make_mask(self, image: NDArray) -> NDArray:
        """
        Create a mask that the bright parts are marked as 255, the rest as 0.

        params
        ------
        image: numpy array

        return
        ------
        frame_threshold: numpy array
        """
        frame_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        frame_threshold = cv2.inRange(frame_hsv, self.low_threshold, self.high_threshold)
        return frame_threshold

    def get_image_mask(self, path: str) -> NDArray:
        image = path
        return self.make_mask(image)
