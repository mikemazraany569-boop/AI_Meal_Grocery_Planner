
from src.vision.image_processor import ImageProcessor

image_path = "D:\\pythonproject\\AI_Meal_Grocery_Planner\\data\\images\\image.jpg"

processor = ImageProcessor()

result = processor.process_image(image_path)

print("Original image:", result["original_shape"])
print("Processed image:", result["processed_shape"])

cv2_image = result["processed"]

import cv2
cv2.imshow("Processed Fridge Image", cv2_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
