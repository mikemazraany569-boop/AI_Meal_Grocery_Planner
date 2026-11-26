from ultralytics import YOLO

model = YOLO("yolo11n.pt")

results = model.predict(
    source="D:\pythonproject\AI_Meal_Grocery_Planner\data\images",
    conf=0.10,
    save=False,
    device="cpu"
)

for result in results:
    print("Detected objects:", len(result.boxes))

    for box in result.boxes:
        class_id = int(box.cls[0])
        print(
            model.names[class_id],
            round(float(box.conf[0]), 3)
        )