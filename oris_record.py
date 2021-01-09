
#Python module for objects and functions related to recording/processing data

import time
import threading
#from multiprocessing import Process

##Imports for filter library
import numpy #numerical analysis library
import scipy #scientific library
from scipy import signal #Signal analysis from scientific library
import scipy.io.wavfile as wav #wave I/O functions from scientific library
import Tkinter as tk
import Queue
import math

import my_adc
from tk_custom2 import *
from OrisFilterFIR import * #Lucias signal filtering

class oris_record():
	
	def __init__(self,root,data_win,stream_q):
		self.root=root
		
		#self.width=sub_width
		#self.height=sub_height

		self.data_win=data_win
		self.data_win.diagnostics()
		self.runtime=0

		self.fs       =0
		self.qual     =""
		self.bpm      =0
		self.rhythm   =""
		self.arr_raw  =[]
		self.arr_filt =[]

		self.rec=tk.BooleanVar()
		self.timer=IntVar()
		self.rec_vals=[]
		self.send_vals=[]

		self.q=stream_q
	
		self.filt=False
		self.stream=False
		self.proc=False
		self.f_shift=0

		self.proc_done=tk.BooleanVar()


	

	# Function for when record start button is pushed
	def start(self,start_btn):
		self.rec.set(True)
		print("TEST")
		self.timer.set(0)
		self.proc_done.set(False)
		start_btn.frame.lower()
		self.data_win.clear_diag()
		self.data_win.place_counter() #Show counter
		self.count()
		if(self.stream):
			t=threading.Thread(target=self.stream_thread)
		else:
			t=threading.Thread(target=self.rec_thread)
		t.start()
		return

	# Function for when record stop button is pushed
	def stop(self,stop_btn=None):
		self.rec.set(False)
		self.timer.set(0)
		#print(self.rec.get())
		self.root.wait_variable(self.proc_done)

		if(stop_btn!=None):
			stop_btn.frame.lower()

			self.data_win.place_diag()
			self.data_win.clear_counter() # Hide Counter

		#while (self.proc_done!=True):
		#	after_id=self.root.after(10,self.stop) 

		#if (self.proc_done.get()):
		data_tuple=(self.bpm,self.rhythm,self.qual)
		print(data_tuple)
		self.data_win.set_data(data_tuple)
		return str(self.fs),str(self.runtime),self.send_vals


	# Counter that increments without freezing gui screen
	def count(self):
		if (self.rec.get()):
			#update info in data window
			print(self.timer.get())
			self.data_win.newData(str(self.timer.get())) 
			self.timer.set(self.timer.get()+1)

			# call function every second instead of using for loop 
			after_id=self.root.after(1000,self.count) 


	def stream_thread(self):
		
		temp_arr=[]
		self.rec_vals=[]
		self.runtime=0

		spi_adc=my_adc.adc()
		starttime=time.time()
		
		i=0
		while (self.rec.get()):
			temp_arr.append(((i/5)%1000)*20)
			#temp_arr.append(int(numpy.sin(6.26*i)/100))
			
			i+=1
			if(len(temp_arr)>20):
				self.q.put(temp_arr)
				temp_arr=[]
				#print("sleep")
				time.sleep(0.01)

		#print(self.q.qsize())
						
		
		self.runtime=time.time()-starttime
		#self.q.put(str(self.runtime))
		#print(self.runtime)

		#for val in range(0,len(temp_arr)):
		#	self.rec_vals.append(spi_adc.convert_input(temp_arr[val]))

		self.send_vals=self.rec_vals
		self.qual     = "Unknown"
		self.bpm      = str(i)
		self.rhythm   = "bangin"
		
		#self.proc_done=True
		self.proc_done.set(True)




	def rec_thread(self):
		temp_arr=[]
		self.rec_vals=[]
		self.runtime=0

		spi_adc=my_adc.adc()
		starttime=time.time()
		
		while (self.rec.get()):
			#if(self.rec.get()==True):
			temp_arr.append(spi_adc.read())
				#print(type(self.rec.get()))
				#time.sleep(0.02)
			#else:
				#print("IN THE IF")
			#	break
		
		self.runtime=time.time()-starttime
		print(self.runtime)

		for val in range(0,len(temp_arr)):
			self.rec_vals.append(spi_adc.convert_input(temp_arr[val]))
		#	print(self.rec_vals[val])

		self.print_data()
		if(self.filt):
			self.send_vals=self.process_data()
			#p=Process(target=self.process_data)
			#p.start()
			#p.join()
			#t=threading.Thread(target=self.process_data)
			#t.start()
		else:
			self.send_vals=self.rec_vals
			self.qual     = "Unknown"
			self.bpm      = str(len(self.rec_vals))
			self.rhythm   = "bangin"
			#self.proc_done.set(True)
		
		#self.proc_done=True
		self.proc_done.set(True)


	def stream_en(self):
		self.stream=True
	def nostream_en(self):
		self.stream=False

	def filter_en(self):
		self.filt=True
	def nofilter_en(self):
		self.filt=False

	def proc_en(self):
		self.proc=True
	def noproc_en(self):
		self.proc=False

	def shift_en(self):
		self.f_shift=25
	def noshift_en(self):
		self.f_shift=0
	
	def process_data(self):

		self.rec_vals.append(self.runtime)
		arr_nd=numpy.asarray(self.rec_vals)

		# Filter and Process data.
		# Returns key heartbeat info and filtered data
		# Courtesy of Lucia I.
		# recording, low, high, freq_shift, S1_beat_thresh, S2_beat_thresh, fast_rate, beat_var, sample_var, processing_enable):
		x1=time.time()
		proc_data=OrisFilterFIR(arr_nd,25,95,self.f_shift,0.8,0.3,120,0.3,0.3,self.proc)
		x2=time.time()
		print(str(x2-x1))

		self.fs       = proc_data[0]
		self.qual     = proc_data[1]
		self.bpm      = proc_data[2]
		self.rhythm   = proc_data[3]
		self.arr_raw  = proc_data[4]
		self.arr_filt = proc_data[5]


		#self.vals_proc=numpy.ndarray.tolist(self.arr_filt)
		return numpy.ndarray.tolist(self.arr_filt)
		#self.send_vals = numpy.ndarray.tolist(self.arr_filt)
		#self.proc_done.set(True)
	
	def print_data(self):
		print
		print "bpm: ",self.bpm
		print "runtime: ",self.runtime
		print "num samples: ",len(self.rec_vals)



	
	

		


