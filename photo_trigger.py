import RPi.GPIO as GPIO
import subprocess
import time
from datetime import datetime

GPIO_PINS = [20, 21]
DEBOUNCE_TIME = 0.2
PHOTO_DIR = "test_photos/"

GPIO.setmode(GPIO.BCM)

for pin in GPIO_PINS:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def take_photo():
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	photo_path = f"{PHOTO_DIR}photo_{timestamp}.jpg"
	subprocess.run(["rpicam-still", "-o", photo_path])
	print(f"Photo takesn and saved to {photo_path}")
	

def scan_gpio_pins():
	for gpio_pin in GPIO_PINS:
		if (GPIO.input(gpio_pin) == GPIO.HIGH):
			return gpio_pin
	
	return -1



try:
	print(f"MOnitoring GPIO pins {GPIO_PINS}...")
	while True:
		active_pin = scan_gpio_pins()
		if (active_pin != -1):
			print(f"HIGH DETECTED FROM PIN {active_pin}")
			take_photo()
			while GPIO.input(active_pin) == GPIO.HIGH:
				time.sleep(DEBOUNCE_TIME)
		time.sleep(0.05)

except KeyboardInterrupt:
	print("Exiting program..")

finally:
	GPIO.cleanup()
