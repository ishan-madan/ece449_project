# lightweightml.py
from pathlib import Path
import cv2
from ultralytics import YOLO

def detect_animal(image_path: str, model_path: str = "best.pt", conf: float = 0.25, iou: float = 0.5):
    """
    Detects animals in an image using a YOLO model.

    Args:
        image_path (str): Path to the image.
        model_path (str): Path to the YOLO model file (default: "best.pt").
        conf (float): Confidence threshold.
        iou (float): IoU threshold.

    Returns:
        dict: {
            "animal_detected": bool,
            "confidences": list of float,
            "annotated_path": str
        }
    """
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")

    # Load the model
    model = YOLO(model_path)

    # Run inference
    results = model(str(img_path), conf=conf, iou=iou)[0]

    confidences = [float(b.conf[0]) for b in results.boxes]
    animal_detected = len(confidences) > 0

    # Save annotated image
    annotated = results.plot()
    out_path = img_path.with_name(img_path.stem + "_out" + img_path.suffix)
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
