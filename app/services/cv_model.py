from ultralytics import YOLO
from collections import Counter

yolo_model = YOLO("app/ml_models/best.pt")

def predict_ingredients(image_path):
    results = yolo_model(image_path)
    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return {}

    class_ids = boxes.cls.cpu().numpy().astype(int)
    detected_objects = [yolo_model.names[i] for i in class_ids]

    counts = Counter(detected_objects)
    ingredient_data = dict(counts)

    print("Detected ingredients:", ingredient_data)

    return ingredient_data