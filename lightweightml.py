# lightweightml.py
from pathlib import Path
import cv2
from ultralytics import YOLO

# global vars
MODEL_PATH = "best.pt"
CONF = 0.25
IOU = 0.1
PHOTO_DIR = "annotated_photos/"
model = YOLO(MODEL_PATH)

def detect_animal(image_path: str):

    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(img_path)

    # Run inference
    results = model(str(img_path), conf=CONF, iou=IOU)[0]

    confidences = [float(b.conf[0]) for b in results.boxes]
    animal_detected = len(confidences) > 0

    # Save annotated image
    annotated = results.plot()
    out_path = f"{image_path}"
    cv2.imwrite(str(out_path), annotated)

    return {
        "animal_detected": animal_detected,
        "confidences": confidences,
        "annotated_path": str(out_path)
    }

# Optional: allow running directly as a script
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 lightweightml.py <image_path>")
        sys.exit(1)
    result = detect_animal(sys.argv[1])
    print(result)
