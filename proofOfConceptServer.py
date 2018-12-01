from _thread import *
from socket import *
import sys, select, struct

#SETUP UDP DATAGRAM SOCKET
SOCK = socket(AF_INET, SOCK_DGRAM)
TTT_SERVER_PORT = 13037
SOCK.bind(('',TTT_SERVER_PORT))

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

def main():
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
		
if __name__ == '__main__':
	main()
