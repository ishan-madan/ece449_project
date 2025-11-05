import RPi.GPIO as GPIO
import subprocess
import time
import requests
from datetime import datetime
from lightweightml import detect_animal

"21: Front PIR(1),26: PIR(2),20: 3, 16: Back PIR(4)"

GPIO_PINS = [20]
CAM_ASSIGN = {20:'0', 21:'1', 26:'2', 16:'0'}
DEBOUNCE_TIME = 0.2
PHOTO_DIR = "test_photos/"


GPIO.setmode(GPIO.BCM)

for pin in GPIO_PINS:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def take_photo(pir_sensor):
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	photo_path = f"{PHOTO_DIR}photo_{pir_sensor}_{timestamp}.jpg"
	subprocess.run(["rpicam-still", "-t", "2000", "--camera", CAM_ASSIGN[pir_sensor], "-o", photo_path])
	print(f"Photo takesn and saved to {photo_path}")
	return detect_animal(photo_path)
	
	

def scan_gpio_pins():
	for gpio_pin in GPIO_PINS:
		if (GPIO.input(gpio_pin) == GPIO.HIGH):
			return gpio_pin
	
	return -1



try:
	print(f"Monitoring GPIO pins {GPIO_PINS}...")
	while True:
		active_pin = scan_gpio_pins()
		if (active_pin != -1):
			print(f"HIGH DETECTED FROM PIN {active_pin}")
			detectionResults = take_photo(active_pin)
			print(detectionResults)
			if detectionResults["animal_detected"] == True:
				print(f"DETER!!! RUN!!!")
				resp = requests.get("http://192.168.68.106/on", timeout = 5)
				print(f"sent deter signal")

			while GPIO.input(active_pin) == GPIO.HIGH:
				time.sleep(DEBOUNCE_TIME)
			print("ALL PINS SCANNING AGAIN")
		time.sleep(0.05)
		

except KeyboardInterrupt:
	print("Exiting program..")

finally:
	GPIO.cleanup()
