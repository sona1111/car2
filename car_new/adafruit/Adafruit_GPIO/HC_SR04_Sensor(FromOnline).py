#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO


# Which GPIO's are used [0]=BCM Port Number [1]=BCM Name [2]=Use [3]=Pin
# ----------------------------------------------------------------------
arrgpio = [(17,"GPIO0","Echo",11),(18,"GPIO7","Trig",12)]



# Set GPIO Channels
# -----------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(arrgpio[0][0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(arrgpio[1][0], GPIO.OUT)
GPIO.output(arrgpio[1][0], False)


# A couple of variables
# ---------------------
EXIT = 0                        # Infinite loop
decpulsetrigger = 0.0001        # Trigger duration
inttimeout = 2100               # Number of loop iterations before timeout called


# Wait for 2 seconds to allow the ultrasonics to settle (probably not needed)
# ---------------------------------------------------------------------------
print "Waiting for 2 seconds....."
time.sleep(2)


# Go
# --
print "Running...."


# Never ending loop
# -----------------
while EXIT == 0:

        # Trigger high for 0.0001s then low
        
	GPIO.output(arrgpio[1][0], True)
	time.sleep(decpulsetrigger)
	GPIO.output(arrgpio[1][0], False)

	# Wait for echo to go high (or timeout)

	intcountdown = inttimeout

	while (GPIO.input(arrgpio[0][0]) == 0 and intcountdown > 0):
		intcountdown = intcountdown - 1

	# If echo is high

	if intcountdown > 0:

		# Start timer and init timeout countdown

		echostart = time.time()
		intcountdown = inttimeout

		# Wait for echo to go low (or timeout)

		while (GPIO.input(arrgpio[0][0]) == 1 and intcountdown > 0):
			intcountdown = intcountdown - 1

		# Stop timer

		echoend = time.time()


		# Echo duration

		echoduration = echoend - echostart

	# Display distance

	if intcountdown > 0:
		intdistance = (echoduration*1000000)/58
		print "Distance = " + str(int(intdistance)) + "cm"
        else:
		print "timeout"
	# Wait at least .01s before re trig (or in this case .1s)

        time.sleep(.1)

