#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
from threading import Thread


# Which GPIO's are used [0]=BCM Port Number [1]=BCM Name [2]=Use [3]=Pin
# ----------------------------------------------------------------------
arrgpio = [(17,"GPIO0","Echo",11),(18,"GPIO7","Trig",12)]
arrgpio2 = [(25,"GPIO0","Echo",22),(4,"GPIO7","Trig",7)]


#constants
Pins = {'P0':(11,17),'P1':(12,18),'P2':(13,21),'P3':(15,22),'P4':(16,23),'P5':(18,24),'P6':(22,25),'P7':(7,4),
'CE1':(26,0),'CE0':(24,0),'SCLK':(23,0),'MISO':(21,0),'MOSI':(19,0),'RDX':(10,0),'TDX':(8,0),'SCL':(5,0),'SDA':(3,0)}


# Set GPIO Channels
# -----------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(arrgpio[0][0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(arrgpio[1][0], GPIO.OUT)
GPIO.output(arrgpio[1][0], False)

GPIO.setup(arrgpio2[0][0], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(arrgpio2[1][0], GPIO.OUT)
GPIO.output(arrgpio2[1][0], False)


# A couple of variables
# ---------------------
          # Number of loop iterations before timeout called


# Wait for 2 seconds to allow the ultrasonics to settle (probably not needed)
# ---------------------------------------------------------------------------
print "Waiting for 2 seconds....."
time.sleep(2)


# Go
# --
print "Running...."




# Never ending loop
# -----------------
class sens(object):


	def __init__(self,gpio,arr):
	
		self.GPIO = gpio
		self.arr = arr

	def run(self):
		# Trigger high for 0.0001s then low
		EXIT = 0                        # Infinite loop
		decpulsetrigger = 0.0001        # Trigger duration
		inttimeout = 2100     
		self.GPIO.output(self.arr[1][0], True)
		time.sleep(decpulsetrigger)
		self.GPIO.output(self.arr[1][0], False)

		# Wait for echo to go high (or timeout)

		intcountdown = inttimeout

		while (self.GPIO.input(self.arr[0][0]) == 0 and intcountdown > 0):
			intcountdown = intcountdown - 1

		# If echo is high

		if intcountdown > 0:

			# Start timer and init timeout countdown

			echostart = time.time()
			intcountdown = inttimeout

			# Wait for echo to go low (or timeout)

			while (self.GPIO.input(self.arr[0][0]) == 1 and intcountdown > 0):
				intcountdown = intcountdown - 1

			# Stop timer

			echoend = time.time()


			# Echo duration

			echoduration = echoend - echostart

		# Display distance

		if intcountdown > 0:
			intdistance = (echoduration*1000000)/58
			print self.arr,
			print "Distance = " + str(int(intdistance)) + "cm"
		else:
			print self.arr,
			print "timeout"
		# Wait at least .01s before re trig (or in this case .1s)

		time.sleep(.1)



s1 = sens(GPIO,arrgpio)
s2 = sens(GPIO,arrgpio2)

while True:
	time.sleep(0.5)
	s1.run()
	time.sleep(0.5)
	s2.run()
	
	
class carMain(object):

    def __init__(self):
        

        self.forwardSens = UsonicSens([Pins['P4'][0]],[Pins['P5'][0]])
        #self.leftSens = UsonicSens([Pins['P0'][0]],[Pins['P1'][0]])
        #self.rightSens = UsonicSens([Pins['P2'][0]],[Pins['P3'][0]])        
        

