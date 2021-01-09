# Oris 2018
# Python functions to setup Bluetooth Client
from bluetooth import *

def discover():
	print ('performing inquiry...')
	nearby_devices=discover_devices(lookup_names=True)
	#print ('found %d devices' % len(nearby_devices))

	#addr_list=[]

	#for addr,name in nearby_devices:
	#    print('%s - %s'% (addr,name))
	#    addr_list.append(addr)

	#print addr_list[0]
	return nearby_devices



#client_socket=BluetoothSocket(RFCOMM)
#client_socket.connect((addr_list[0],3))
#client_socket.send("hello world")
#client_socket.close

    


