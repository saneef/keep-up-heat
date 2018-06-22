#!/usr/bin/env python

import time
import sys
from max6675 import MAX6675, MAX6675Error
import RPi.GPIO as GPIO

cs_pin = 8
clock_pin = 11
data_pin = 9
units = "c"
relay_pin = 16

thermocouple = None

temp_level = {
	'LOW': 150,
	'MED': 180,
	'HIGH': 200,
	'COOL': 40
}

probe_delay = .25 # Seconds. Minimum .25 is required for themocouple to work

profile = [
	{'minute': 0, 'temp_level': temp_level['LOW']},
	{'minute': 2, 'temp_level': temp_level['MED']},
	{'minute': 4, 'temp_level': temp_level['HIGH']},
	{'minute': 9, 'temp_level': temp_level['COOL']},
]


# profile = [
# 	{'minute': 0, 'temp_level': temp_level['LOW']},
# 	{'minute': .1, 'temp_level': temp_level['MED']},
# 	{'minute': .4, 'temp_level': temp_level['HIGH']},
# 	{'minute': .8, 'temp_level':  20 },
# ]

checkpoints = sorted(profile, key=lambda x: x['minute'])

def init_relay():
	GPIO.setup(relay_pin, GPIO.OUT)

def relay_on():
	GPIO.output(relay_pin, GPIO.HIGH)

def relay_off():
	GPIO.output(relay_pin, GPIO.LOW)

def cleanup_relay():
	GPIO.cleanup(relay_pin)

def init_thermocouple():
	global thermocouple
	thermocouple = MAX6675(cs_pin, clock_pin, data_pin, units)

def cleanup_thermocouple():
	if thermocouple != None:
		thermocouple.cleanup()

def get_next_setting(start_time, current_time, checkpoint=0):
	next_checkpoint = checkpoint

	for point in checkpoints:
		if (point["minute"] * 60 + start_time) < current_time:
			next_checkpoint = checkpoints.index(point)
	
	return next_checkpoint

def main():
	init_thermocouple()
	init_relay()
	current_checkpoint = 0
	start_time = time.time()
	while True:
		current_temp = thermocouple.get()
		current_time = time.time()
		current_checkpoint = get_next_setting(start_time, current_time, current_checkpoint)
		dest_temp = checkpoints[current_checkpoint]["temp_level"]
		message = 'Current: %s DegC	Destination: %s DegC	Seconds: %.2f' % (current_temp, dest_temp, current_time - start_time)
		print message
		if current_temp < dest_temp:
			relay_on()
		else:
			relay_off()
		time.sleep(probe_delay)

def cleanup():
	print "Cleaning up..."
	cleanup_thermocouple()
	cleanup_relay()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print "Exitting..."
		cleanup()
	sys.exit(0)

