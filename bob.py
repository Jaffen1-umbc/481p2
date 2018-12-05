from _thread import *	#_thread for python3, thread for python 2.7
from socket import *
from random import shuffle 
import sys, select, struct, time
from traceback import print_exc

TTT_SERVER_PORT = 13037		
#SETUP UDP DATAGRAM SOCKET
SOCK = socket(AF_INET, SOCK_DGRAM)
SOCK.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SOCK.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
SOCK.setblocking(False) 
#SOCK.settimeout(1)
#SOCK.setblocking(True)
SOCK.bind(('',TTT_SERVER_PORT))

def getline():
	i, o, e = select.select([sys.stdin],[],[], 0.0001)
	for s in i:
		if s == sys.stdin:
			client_input = sys.stdin.readline()
			return client_input
			
	return None
	
while 1:
	try:
		msg, addr = SOCK.recvfrom(1024)
		#if message:
		print (addr, "> ", message)
			
	except:
		print("empty")
	
	cmd_line_input = getline()
	if cmd_line_input is not None:
		SOCK.sendto(cmd_line_input.encode(), ('',TTT_SERVER_PORT))
