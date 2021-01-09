
#Python module for objects and functions related to recording/processing data

import threading
from bluetooth import *
import re
import time

from tk_custom2 import *
import my_btClient as bt

class oris_bt():
	def __init__(self,root,dev_window,tx_btn,recframe,stream_q):
		self.root=root
		self.dev_window=dev_window
		self.tx_btn=tx_btn
		self.recframe=recframe
		self.tick=False

		self.bt_devs=[]
		self.dev_btns=[]
		self.btn_idx=0
		self.btn_idx_old=100

		self.msg="Searching"
		self.addr_sel=""
		self.fs=""
		self.runtime=""
		self.data=[]

		self.data_len=59

		self.stream_en=True
		self.q=stream_q
		


	def enable(self,enable_btn):
		self.tick=True
		self.msg="Searching"
		enable_btn.frame.lower()
		self.loadingMsg()
		t=threading.Thread(target=self.btThread)
		t.start()
	
	def disable(self,disable_btn):
		self.tick=False
		disable_btn.frame.lower()
		for dev in self.dev_btns:
			dev.frame.pack_forget()
			dev.frame.destroy()
		self.bt_devs=[]
		self.dev_btns=[]
		self.btn_idx=0

		self.tx_btn.frame.grid_forget()

	def btThread(self):
		self.bt_devs=bt.discover()
		self.tick=False

	def loadingMsg(self):
		test=re.match("(\w+)(\.\.\.)",self.msg)## reset after 3 ticks
		if (self.tick):
			if (test):
				self.msg=test.group(1)
			else:
				self.msg=self.msg+"."

			self.dev_window.message(self.msg)
			after_id=self.root.after(800,self.loadingMsg)

		else:
			self.msg="Devices"
			self.dev_window.message(self.msg)
			if(len(self.bt_devs)!=0):
				for addr,name in self.bt_devs:
					print ('%s : %s' %(addr,name))
					dev1=winlabel(self.dev_window.fetch(),name)
					dev1.label.bind("<Button-1>",lambda event,addr=addr,dev_idx=self.btn_idx: self.btconn(addr,dev_idx))
					self.dev_btns.append(dev1)
					self.btn_idx+=1

			#else say 'no devices found' for a brief period of time
			

	def btconn(self,addr,dev_idx):
		self.addr_sel=str(addr)
		
		# If button is pressed change colour to blue
		#self.dev_btns[dev_idx].label.config(bg="blue")
		self.dev_btns[dev_idx].cfg("blue","white")

		# If button was previously pressed then change old button back to blue
		if(self.btn_idx_old<len(self.dev_btns)):
			#self.dev_btns[self.btn_idx_old].label.config(bg="lightblue")
			self.dev_btns[self.btn_idx_old].cfg("lightblue","black")


		self.btn_idx_old=dev_idx

		#show button on record page to transfer data via bluetooth
		self.tx_btn.frame.grid(row=1,column=0,sticky=N,pady=(70,0),padx=(100,0))



	def dataTx(self,fs,runtime,data):
		self.fs=fs
		self.runtime=runtime	
		self.data=data

		# Initialize Bluetooth Socket
		try:
			self.client_socket=BluetoothSocket(RFCOMM)
			self.client_socket.connect((self.addr_sel,3)) # initiate connection when tx button pressed
			print "Connected to ",self.addr_sel
			# Begin Thread for data transfer
			t=threading.Thread(target=self.txThread)
			t.start()
		except Exception as msg:
			print(msg)
		return


	def startStream(self):
		try:
			if(self.addr_sel!=""):
				self.stream_en=True
				self.client_socket=BluetoothSocket(RFCOMM)
				self.client_socket.connect((self.addr_sel,3)) # initiate connection when tx button pressed
				print "Connected to ",self.addr_sel
				 #Begin Thread for data transfer
				t=threading.Thread(target=self.streamThread)
				t.start()
			else:
				print("nneed an address!")
		except Exception as msg:
			print(msg)
		return

	def stopStream(self,runtime):
		self.runtime=runtime
		self.stream_en=False
		print(runtime)
		

	def streamThread(self):
                    
		send_str=""
		try:
			while (self.stream_en or not self.q.empty()):
				if(not self.q.empty()):
					send_str=",".join(map(str,self.q.get()))
					send_str+=","
					#print(send_str)
					self.client_socket.send(send_str)
					time.sleep(0.01)

			self.client_socket.send("runtime: "+self.runtime)
			print(self.runtime)			
			print "done"
			self.client_socket.close()
		except Exception as msg:
			print(msg)
		#finally:
		#	self.tx_btn.frame.grid(row=1,column=0,sticky=N,pady=(70,0),padx=(100,0))
			
			

	def txThread(self):
		#try-except here to catch bluetooth errors for user
    # add some hide button stuff so user knows when sending
		#send_str="data: "
		try:
			self.tx_btn.frame.grid_forget()
			send_str=""
			x1=time.time()
			for line in range(0,len(self.data)):
				send_str+=str(self.data[line])
				if (line%(self.data_len)!=0): #amount of data sent is configurable
					send_str+=","
				else:
					send_str+=","
					#print "!"+send_str
					self.client_socket.send(send_str)
					send_str="" 
					time.sleep(0.01)

			x2=time.time()
			print("tx_time: "+str(x2-x1))
				
			self.client_socket.send("runtime: "+self.runtime)
			#self.client_socket.send("fs: "+self.fs)
			print(self.runtime)			
			print "done"
			self.client_socket.close()
		except Exception as msg:
			print(msg)
		finally:
			self.tx_btn.frame.grid(row=1,column=0,sticky=N,pady=(70,0),padx=(100,0))
			
			




		
