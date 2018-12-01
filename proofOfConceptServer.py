from _thread import *
from socket import *
import sys, select, struct

#SETUP UDP DATAGRAM SOCKET
#SOCK = socket(AF_INET, SOCK_DGRAM)
#TTT_SERVER_PORT = 13037
#SOCK.bind(('',TTT_SERVER_PORT))

ACTIVE_GAMES = []	#the global array to store the active games
CLIENT_QUEUE = []
UNIQUE_ID_COUNTER = 0	#the global uniqie ID index to ensure no duplicate games

def myObj:
	def __init__(self, addr, uid):
		self.addr = addr
		self.uid = uid

		
		
def get_active_game_index_or_none(addr):
	for i, game in enumerate(ACTIVE_GAMES):
		if game.addr == addr:
			return i
		
	return None

def main2():
	global UNIQUE_ID_COUNTER


	print ('The server is ready to receive connections')
	try:
		while 1:
			#receive a message.
			msg, addr = SOCK.recvfrom(2048)
			print("\nAddress: ", addr, "\nSent: ", msg)
			'''CLIENT_QUEUE.append((addr, msg))
			#check if game already exists from the sender
			current_index = get_active_game_index_or_none(addr)
			if current_index is not None:
				ACTIVE_GAMES[current_index].pass_client_message(msg)
			else:
				#create a game state
				ACTIVE_GAMES.append(TTT_Game(addr, UNIQUE_ID_COUNTER))
				UNIQUE_ID_COUNTER += 1
			
			#create new thread for this client
			#UDP? start_new_thread(game_thread,(addr, ACTIVE_GAMES[-1]))
			'''
			
	except KeyboardInterrupt:
		#dont crash program... allow for cleanup
		print("\nCLOSING DOWN TIC-TAC-TOE SERVER")
		#UDP? for v in ACTIVE_GAMES:
		#UDP? 	v.conn.close()
		#UDP? SOCK.close()
		sys.exit(0)

# Math Server
import struct
import socket

def main():
	udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp_socket.bind(("localhost", 5000))

	while True:
		# Receive and unpack the data
		data, address = udp_socket.recvfrom(512)
		try:
			op, a, b = struct.unpack(">3sii", data)
			op = op.decode('ascii')

		except struct.error:
			# Handle the case where we receive a malformed packet
			print("Unable to unpack packet")

		else:
		# Perform the calculation
			result = 0
			success = 0
		if op == "add":
			result = a + b
			success = 1
		elif op == "sub":
			result = a - b
			success = 1
		elif op == "mul":
			result = a * b
			success = 1
		#catch the divide by zero
		elif op == "div" and b != 0:
			result = a // b
			success = 1

		# Pack and send the result
		binary = struct.pack(">bi", success, result)
		udp_socket.sendto(binary, address)
	
if __name__ == '__main__':
	main()
