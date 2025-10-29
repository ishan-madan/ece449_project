import RPi.GPIO as GPIO
import subprocess
import time
from datetime import datetime
from PIL import Image
import io
import numpy as np
from test_ml import detect_animal  # assuming detect_animal can accept numpy arrays

GPIO_PINS = [20]
CAM_ASSIGN = {20:'0', 21:'1', 26:'2'}
DEBOUNCE_TIME = 0.2

GPIO.setmode(GPIO.BCM)
for pin in GPIO_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def take_photo_in_memory(pir_sensor):
    """Capture photo into memory and feed directly to ML model."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"Capturing photo from sensor {pir_sensor}...")

    # Run raspistill and capture stdout as bytes
    result = subprocess.run(
        ["rpicam-still", "-t", "2000", "--camera", CAM_ASSIGN[pir_sensor], "-o", "-"],  # '-' outputs to stdout
        stdout=subprocess.PIPE
    )
    
    # Convert bytes to PIL image
    image = Image.open(io.BytesIO(result.stdout))
    
    # Convert to numpy array and preprocess for ML
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)  # add batch dimension if needed
    
    print("IMage shape:", image_array.shape)
    
    # Run ML model
    predictions = detect_animal(image_array)
    print(f"Predictions: {predictions}")

def scan_gpio_pins():
    for gpio_pin in GPIO_PINS:
        if GPIO.input(gpio_pin) == GPIO.HIGH:
            return gpio_pin
    return -1

try:
    print(f"Monitoring GPIO pins {GPIO_PINS}...")
    while True:
        active_pin = scan_gpio_pins()
        if active_pin != -1:
            print(f"HIGH DETECTED FROM PIN {active_pin}")
            take_photo_in_memory(active_pin)
            while GPIO.input(active_pin) == GPIO.HIGH:
                time.sleep(DEBOUNCE_TIME)
            print("ALL PINS SCANNING AGAIN")
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting program..")
finally:
    GPIO.cleanup()

