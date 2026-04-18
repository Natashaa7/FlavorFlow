# app/services/cv_model.py
from PIL import Image
import torch
import torchvision.transforms as transforms
from ultralytics import YOLO

# Load YOLO model (object detection)
yolo_model = YOLO("app/model/final_model.pt")

# Define your custom ingredient classes
CLASS_NAMES = [
    "tomato", "onion", "garlic", "carrot",
    "chicken", "beef", "egg"
]

# Image preprocessing for PyTorch model
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def predict_ingredients(image_path):
    yolo_results = yolo_model(image_path)  # your YOLO inference
    boxes = yolo_results[0].boxes  # Boxes object
    class_ids = boxes.cls.cpu().numpy().astype(int)  # convert to integer IDs
    detected_objects = [yolo_model.names[i] for i in class_ids]  # map IDs to names
    return detected_objects