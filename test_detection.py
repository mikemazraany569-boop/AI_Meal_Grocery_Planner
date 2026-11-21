
from src.vision.ingredient_detector import IngredientDetector

image_path = "D:\\pythonproject\\AI_Meal_Grocery_Planner\\data\\images\\image.jpg"

detector = IngredientDetector()

detections = detector.detect(image_path)

print("\nDETECTED OBJECTS")
print("================")

if not detections:
    print("No objects detected.")

for item in detections:
    print(
        f"{item['label']} | "
        f"Confidence: {item['confidence']} | "
        f"Box: {item['box']}"
    )
