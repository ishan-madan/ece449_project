# lightweightml.py
from pathlib import Path
import cv2
from ultralytics import YOLO
import numpy as np

# Load model globally so you don’t reload every call
MODEL_PATH = "best.pt"
CONF = 0.25
IOU = 0.5
PHOTO_DIR = "annotated_photos/"
model = YOLO(MODEL_PATH)

def detect_animal(image):
    """
    Detect animals in an image.
    `image` can be:
        - str / Path -> path to image file
        - np.ndarray -> image in memory (H, W, C) RGB or BGR
    """
    # Convert path to numpy array if necessary
    if isinstance(image, (str, Path)):
        img_path = Path(image)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {img_path}")
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        save_base_path = img_path.stem
    elif isinstance(image, np.ndarray):
        img = image
        save_base_path = "memory_image_" + str(int(time.time()))
    else:
        raise ValueError("`image` must be a file path or a NumPy array")

    # Run inference
    results = model(img, conf=CONF, iou=IOU)[0]

    confidences = [float(b.conf[0]) for b in results.boxes]
    animal_detected = len(confidences) > 0

    # Save annotated image
    annotated = results.plot()
    out_filename = f"{save_base_path}_out{'_true' if animal_detected else '_false'}.jpg"
    out_path = Path(PHOTO_DIR) / out_filename
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

