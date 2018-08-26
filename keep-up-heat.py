#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import datetime
import RPi.GPIO as GPIO
from max31855.max6675 import MAX6675, MAX6675Error
from profile import profile

cs_pin = 8
clock_pin = 11
data_pin = 9
relay_pin = 16
units = "c"

fixed_heat_level = None
thermocouple = None

probe_delay = .25 # Seconds. Minimum .25 is required for themocouple to work

profile = profile(sys.argv)

checkpoints = sorted(profile, key=lambda x: x['minute'])

def heat_from_args(argv):
	try:
		index =  argv.index('--temp')
	except ValueError:
		return None

	if (index > 0):
		temp = argv[index + 1]
		if temp != None:
			return float(temp)

	return None

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
	fixed_heat_level = heat_from_args(sys.argv)
	while True:
		current_temp = thermocouple.get()
		current_time = time.time()
		if fixed_heat_level != None:
			dest_temp = fixed_heat_level
		else:
			current_checkpoint = get_next_setting(start_time, current_time, current_checkpoint)
			dest_temp = fixed_heat_level if fixed_heat_level != None else  checkpoints[current_checkpoint]["temp"]
		elapsed_time = datetime.timedelta(seconds=round(current_time - start_time))
		message = "[%s] %.2f°C (%s°C)"  % (elapsed_time, current_temp, dest_temp)
		sys.stdout.write(message)
		ret =  "\r" * (len(message) + 1)
		if current_temp < dest_temp:
			relay_on()
		else:
			relay_off()
		time.sleep(probe_delay)
		sys.stdout.write(ret)
		sys.stdout.flush()

def cleanup():
	print "\nCleaning up GPIO..."
	cleanup_thermocouple()
	cleanup_relay()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		cleanup()
		print "Exitting..."
	sys.exit(0)

