
# Functions for setting up SPI and reading the ADC 

import spidev
from numpy import interp
from time import sleep
import RPi.GPIO as GPIO


# testing spi conn   
#spi = spidev.SpiDev()
#spi.open(0,1)


class adc:

	channel=1

	def __init__(self):
		self.spi=spidev.SpiDev()
		self.spi.open(1,0)
		self.spi.max_speed_hz = 32000
		

	def read(self):
		input=self.spi.xfer2([1,(8+adc.channel)<<4,0])
		#print(input)
		return input

	# This is needed so that the input data read is in a usable form
	def convert_input(self,input):
		data=((input[1]&3) << 8) + input[2]
		return data

	def close(self):
		self.spi.close()


# read mcp3008 data
def analogInput(channel):
	spi = spidev.SpiDev()
	spi.open(1,0)
	spi.max_speed_hz = 30500
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
        spi.close()
	return data



#while True: #testing adc 
#	output = analogInput(0)
#	print(output)
#	sleep(0.1)
