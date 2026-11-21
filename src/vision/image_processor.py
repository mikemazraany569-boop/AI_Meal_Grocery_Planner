
import cv2
from pathlib import Path


class ImageProcessor:

    def __init__(self, target_size=(640, 640)):
        self.target_size = target_size

    def load_image(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(
                "Could not read image. Check its format."
            )

        return image

    def resize_image(self, image):
        return cv2.resize(
            image,
            self.target_size,
            interpolation=cv2.INTER_AREA
        )

    def process_image(self, image_path):
        image = self.load_image(image_path)
        resized = self.resize_image(image)

        return {
            "original": image,
            "processed": resized,
            "original_shape": image.shape,
            "processed_shape": resized.shape
        }
