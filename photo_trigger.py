import RPi.GPIO as GPIO
import subprocess
import time
import requests
from datetime import datetime
import json
from lightweightml import detect_animal

"21: Front PIR(1),26: PIR(2),20: 3, 16: Back PIR(4)"

# store gpio pins to listen to and assign cameras to those pins
GPIO_PINS = [20, 21, 26, 16]
# GPIO_PINS = [20]
CAM_ASSIGN = {16:'0', 26:'1', 21:'2', 20:'3'}

# the amount of time we will wait after a pin goes low before allowing it to scan again
DEBOUNCE_TIME = 0.2

# the maximum amt of time we wait for a pin to be scanning high before allowing it to scan again
MAX_HIGH_DURATION = 30.0

# photo directory to save photos into
PHOTO_DIR = "/home/ratwranglers/Desktop/ece449_project/test_photos"

GPIO.setmode(GPIO.BCM)

for pin in GPIO_PINS:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# track which pin is triggered and when it was triggered and what time it goes low
triggered_pin = None
trigger_time = None
low_time = None

# take photo method takes a photo and stores it. Outputs the result of the ML model
def take_photo(pir_sensor):
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	photo_path = f"{PHOTO_DIR}photo_{pir_sensor}_{timestamp}.jpg"
	subprocess.run(["rpicam-still", "-t", "2000", "--camera", CAM_ASSIGN[pir_sensor], "-o", photo_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	print(f"Photo takesn and saved to {photo_path}")
	return detect_animal(photo_path)


# returns if any of the scannable GPIO pins are active
def scan_gpio_pins(pins_to_scan):
	for gpio_pin in pins_to_scan:

		if GPIO.input(gpio_pin) == GPIO.HIGH:
			return gpio_pin
	
	return -1

# checks to see if any given pin should be unblocked
# returns a boolean for whether all pins should be unblocked or an array of the pins to be unblocked
def check_unblock_conditions():
	global triggered_pin, trigger_time, low_time

	if triggered_pin is None:
		return True, GPIO_PINS

	# store the time since trigegring and the current state of the pin
	elapsed_since_trigger = time.time() - trigger_time
	triggered_pin_state = GPIO.input(triggered_pin)

	# track when the pin goes low
	if triggered_pin_state == GPIO.LOW and low_time is None:
		low_time = time.time()
		print(f"Pin {triggered_pin} went LOW at {low_time}")

	# if a pin goes HIGH again, reset the low_time
	if triggered_pin_state == GPIO.HIGH and low_time is not None:
		print(f"Pin {triggered_pin} went HIGH again, resetting the low_time")
		low_time = None

	# condition 1: triggered pin went low and debounce time has passed since going low -> all pins now unblocked
	if triggered_pin_state == GPIO.LOW and low_time is not None:
		elapsed_since_low_time = time.time() - low_time
		if elapsed_since_low_time > DEBOUNCE_TIME:
			print(f"Pin {triggered_pin} has been LOW for {elapsed_since_low_time:.2f}s (>= {DEBOUNCE_TIME}s) - unblocking ALL pins")
			triggered_pin = None
			trigger_time = None
			low_time = None
			return True, GPIO_PINS

	# condition 2: max duration has been exceeded while the same pin has remained HIGH
	if triggered_pin_state == GPIO.HIGH and elapsed_since_trigger >= MAX_HIGH_DURATION:
		print(f"Pin {triggered_pin} still HIGH after {MAX_HIGH_DURATION}s - unblocking all pins EXCEPT {triggered_pin}")

		# reset all pins EXCEPT the triggered pin
		return False, [p for p in GPIO_PINS if p != triggered_pin]

	# if neither condition is met, return false and keep all pins blocked
	return False, None

try:
	print(f"Monitoring GPIO pins {GPIO_PINS}...")
	print(f"Debounce time: {DEBOUNCE_TIME}s, Max high duration: {MAX_HIGH_DURATION}s")

	while True:
		# get the pins which can be scanned/unblocked
		all_unblocked, scannable_pins = check_unblock_conditions()

		# only scan if we have pins available to scan
		if scannable_pins is not None and len(scannable_pins) > 0:
			# get active pin
			active_pin = scan_gpio_pins(scannable_pins)

			# if there is an active pin
			if active_pin != -1:
				# output that the pin is HIGH
				print(f"HIGH DETECTED FROM PIN {active_pin}")

				# block ALL pins immediately
				triggered_pin = active_pin
				trigger_time = time.time()
				low_time = None
				print(f"ALL pins blocked at {time.time()}")

				# take photo and process results
				detectionResults = take_photo(active_pin)
				print(json.dumps(detectionResults, indent=2, default=str))
				

				# if animal is detected, trigger wifi call to deter system
				if detectionResults["animal_detected"] == True:
					print(f"DETER!!! RUN!!!")
					try:
						resp = requests.get("http://192.168.68.106/on", timeout=5)
						print(f"sent deter signal")
					except Exception as e:
						print(f"Error sending deter signal: {e}")

			time.sleep(0.05)
		

except KeyboardInterrupt:
	print("Exiting program..")

finally:
	GPIO.cleanup()
