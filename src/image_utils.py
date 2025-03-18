"""Image filtering and processing utilities."""

import pathlib
import typing as tp

import cv2
import numpy as np
from numpy import ma
from pdf2image import convert_from_path

import geometry_utils

SUPPORTED_IMAGE_EXTENSIONS = [".tiff", ".tif", ".pdf"]


def convert_to_grayscale(image: np.ndarray,
                         save_path: tp.Optional[pathlib.PurePath] = None
                         ) -> np.ndarray:
    """Convert an image to grayscale.

    If `save_path` is provided, will save the resulting image to this location
    as "grayscale.jpg". Used for debugging purposes.
    """
    result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if save_path:
        save_image(save_path / "grayscale.jpg", result)
    return result


def remove_hf_noise(image: np.ndarray,
                    save_path: tp.Optional[pathlib.PurePath] = None
                    ) -> np.ndarray:
    """Blur image slightly to remove high-frequency noise.

    If `save_path` is provided, will save the resulting image to this location
    as "noise_filtered.jpg". Used for debugging purposes.
    """
    # This value for sigma was chosen such that sigma=sqrt(2) for 2500px images.
    # Still needs more verification for low-res images.
    # NOTE: This assumes the image is roughly A4 paper shaped. If this fails,
    # consider switching to using the mean of the image dimensions.
    sigma = min(get_dimensions(image)) * (5.6569e-4)
    result = cv2.GaussianBlur(image, (0, 0), sigmaX=sigma)
    if save_path:
        save_image(save_path / "noise_filtered.jpg", result)
    return result


def detect_edges(image: np.ndarray,
                 save_path: tp.Optional[pathlib.PurePath] = None
                 ) -> np.ndarray:
    """Detect edges in the image.

    If `save_path` is provided, will save the resulting image to this location
    as "edges.jpg". Used for debugging purposes.
    """
    low_threshold = 100
    result = cv2.Canny(image,
                       low_threshold,
                       low_threshold * 3,
                       L2gradient=True,
                       edges=3)
    if save_path:
        save_image(save_path / "edges.jpg", result)
    return result


def find_contours(edges: np.ndarray) -> np.ndarray:
    """Find the contours in an edge-detected image."""
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)
    return contours


def get_images(image_paths: tp.List[pathlib.PurePath], 
               save_path: tp.Optional[pathlib.PurePath] = None
               ) -> tuple[tp.List[np.ndarray], tp.List[str], tp.List[str]]:
    """parses multi-page images into a name and image tuple. If `save_path` 
    is provided, will save the resulting image to this location as 
    "original.jpg". Used for debugging purposes.
    """
    images = []
    images_name = []
    images_type = []
    for image_path in image_paths:
        pages = []
        if image_path.suffix.lower() == ".pdf":
            PIL_formatted_pages = convert_from_path(str(image_path))
            for PIL_formatted_page in PIL_formatted_pages:
                pages.append(np.array(PIL_formatted_page))
        else:
            pages = cv2.imreadmulti(str(image_path), flags=cv2.IMREAD_COLOR)[1]
        if len(pages) > 0: 
            for i in range(len(pages)):
                images.append(pages[i])
                images_name.append(str(image_path.stem) + "_" + str(i+1))
                images_type.append(str(image_path.suffix)[1:])
                if save_path:
                    save_image(save_path / "original.jpg", result)
    return (images, images_name, images_type)


def save_image(path: pathlib.PurePath, image: np.ndarray):
    """Save the given image at the provided path. Path must be the full target
    including file extension."""
    cv2.imwrite(str(path), image)


def find_polygons(image: np.ndarray,
                  save_path: tp.Optional[pathlib.PurePath] = None
                  ) -> tp.List[geometry_utils.Polygon]:
    """Returns a list of polygons found in the image."""
    edges = detect_edges(image, save_path=save_path)
    all_contours = find_contours(edges)
    polygons = [
        geometry_utils.approx_poly(contour) for contour in all_contours
    ]
    return polygons


def get_dimensions(image: np.ndarray) -> tp.Tuple[int, int]:
    """Returns the dimensions of the image in `(width, height)` form."""
    return image.shape[0], image.shape[1]


def threshold(image: np.ndarray,
              save_path: tp.Optional[pathlib.PurePath] = None) -> np.ndarray:
    """Convert an image to pure black and white pixels by thresholding.

    If `save_path` is provided, will save the resulting image to this location
    as "thresholded.jpg". Used for debugging purposes.
    """
    gray_image = convert_to_grayscale(image)
    _, result = cv2.threshold(gray_image, 0, 255,
                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    if save_path:
        save_image(save_path / "thresholded.jpg", result)
    return result


def prepare_scan_for_processing(image: np.ndarray,
                                save_path: tp.Optional[pathlib.PurePath] = None
                                ) -> np.ndarray:
    """Shortcut to prepare an image for processing.

    If `save_path` is provided, will save the resulting image to this location
    as "prepared.jpg". Used for debugging purposes.
    """
    without_noise = remove_hf_noise(image, save_path=save_path)
    result = threshold(without_noise, save_path=save_path)
    return result


def get_fill_percent(matrix: tp.Union[np.ndarray, ma.MaskedArray]) -> float:
    """Get the percent of the pixels in the B&W matrix that are not white."""
    try:
        return 1 - (matrix.mean() / 255)
    except ZeroDivisionError:
        return 0


def dilate(image: np.ndarray,
           save_path: tp.Optional[pathlib.PurePath] = None) -> np.ndarray:
    """Dilate the image.

    If `save_path` is provided, will save the resulting image to this location
    as "dilated.jpg". Used for debugging purposes.
    """
    # Dilation is done with a static kernel size of 3 x 3 pixels. This means it
    # has a far more significant effect on smaller images, which helps to
    # counter the detail loss when Gaussian filtering small images that already
    # have too little detail.
    result = cv2.dilate(image, np.ones((3, 3), np.uint8), iterations=1)
    if save_path:
        save_image(save_path / "dilated.jpg", result)
    return result


def bw_to_bgr(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)


def draw_polygons(image: np.ndarray,
                  polygons: tp.List[geometry_utils.Polygon],
                  full_save_path: tp.Optional[pathlib.PurePath] = None,
                  thickness: int = 1) -> np.ndarray:
    """Draw all the polygons on the image (for debugging) and return or save the result."""
    points = [np.array([[p.x, p.y] for p in poly], np.int32).reshape((-1, 1, 2)) for poly in polygons]
    result = cv2.polylines(bw_to_bgr(image), points, True, (0, 0, 255), thickness)
    if full_save_path:
        save_image(full_save_path, result)
    return result
