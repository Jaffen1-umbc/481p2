from socket import *
import sys, struct, select, os, time
from queue import *
from threading import *


#CONSTANTS & GLOBALS
#SETUP UDP DATAGRAM SOCKET
client_socket = socket(AF_INET, SOCK_DGRAM)

TTT_SERVER_PORT = 13037
SERVER_ADDRESS = ('', TTT_SERVER_PORT)

SERVER_MARK = 1
CLIENT_MARK = 2
TTT_PRTCL_TERMINATE = 0
TTT_PRTCL_EXPECTING_NO_RESPONSE = 1
TTT_PRTCL_EXPECTING_INT_RESPONSE = 2
TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE = 3
TTT_PRTCL_RESEND = 4
TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE = 37	#37 is the size of a packed !I value 


def recv_server_response():
	'''
	RECIEVING FROM SERVER TO CLIENT: 
		RECV PACKED: MESSAGE RESPONSE LENGTH
		unpack '!I' and .recv that many bytes
		RECV: MESSAGE
		RECV PACKED: EXPECTING RESPONSE VAL
		unpack '!i' and add to ret_list
	Receives the size of the next incoming response, and the next incoming response.

	RETURNS:
		server_response -- the response received.
		[<EXPECTING RESPONSE>, <MESSAGE>]
		<EXPECTING RESPONSE> Valid values are:
			TTT_PRTCL_TERMINATE
				-- connection will be closing, message is the last message from the server.
			TTT_PRTCL_EXPECTING_NO_RESPONSE
				-- expecting no response, message is just a message.
			TTT_PRTCL_EXPECTING_INT_RESPONSE
				-- expecting a single digit integer response, message is a prompt for the user
			TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE
				-- expecting the TTT_PRTCL_REQUEST_FIRST_ARGS response, message is instructions.
		<MESSAGE> Valid values are:
			A string with a message.
	'''
	ret_list = []
	try:
		#recv a message length from the server
		server_msg_len_buf = client_socket.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE) #get size of 37
		if not server_msg_len_buf:
			return None
		server_msg_len, = struct.unpack("!I", server_msg_len_buf[0])
	
		#print("Recving msg of len: ", server_msg_len) #TODO DEBUG  
	
		#recv a message from the server	
		server_msg = client_socket.recvfrom(int(server_msg_len)) #get the variable sized message
		ret_list.append(server_msg[0].decode())

		#print("Recved msg: ", server_msg[0])	#TODO DEBUG
	
		#recv an int value of the expexted response value
		expecting_response_buf = client_socket.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE) #get size of 37
		if not expecting_response_buf:
			return None
		expecting_response, = struct.unpack("!I", expecting_response_buf[0])
	
		#print("Expecting response val: ", expecting_response)	#TODO DEBUG
	
		#add expcted response value to list	
		ret_list.insert(0, expecting_response)
		
		return ret_list
	except:
		pass
	
	return None 
	

def send_single_digit_response(num, addr):
	'''
	Sends an unsigned int value to the server
	
	SENDING FROM CLIENT TO SERVER:
		pack single digit val '!I'
		SEND PACKED: SINGLE DIGIT VAL
	
	'''
	client_socket.sendto(struct.pack('!I', num), addr)
	
def get_server_response_thread(shared_queue):
	'''
	Thread that gets a message from the client and puts it into the queue.
	'''
	while True:
		try:
			while shared_queue.qsize() == 0:
				#print("Listining for server input")
				server_response = recv_server_response()
				if server_response != None:
					shared_queue.put((SERVER_MARK, server_response))
		except KeyboardInterrupt:
			return None
		except:
			pass

	return None

def get_user_response_thread(shared_queue):
	'''
	Thread that gets user input and if it is valid, it will put it into the queue.
	'''
	
	while True:
		try:
			while shared_queue.qsize() == 0:
				#print("Listining for user input")
				i, o, e = select.select([sys.stdin],[],[], 0.0001)
				for s in i:
					if s == sys.stdin:
						client_input = sys.stdin.readline()
						try:
							#check valid user input
							temp = int(client_input[0])
							shared_queue.put((CLIENT_MARK, temp))
						except:
							pass
		except KeyboardInterrupt:
			return None
		except:
			pass
					
#	raise KeyboardInterrupt
	return None

def clear_screen():
	try:
		os.system('cls' if os.name == 'nt' else 'clear')
	except:
		try:
			print( chr(27) + "[2J" )
		except:
			print("Clearing screen...")
			print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")


	
def parse_cmd_line_args(argv):
	'''
	returns an unsigned int value representing if the client has first move or not

	argv -- list with [-c] [-s serverIP]

	RETURNS: 
		<START_MARK>, <SERVER_IP>
		<START_MARK> Valid values are:
			0 -- server has first move
			1 -- client has first move

		<SERVER_IP>
			the server ip
	'''
	
	ttt_server_name = None
	
	try:
		#set who goes first
		start_mark = 0		#default is the server starts
		if "-c" in argv:
			start_mark = 1
			
		#get server ip
		for i in range(len(argv)): #for some odd reason i was getting errors with enumerate(argv)
			if argv[i] == "-s":
				ttt_server_name = argv[i + 1]
				
	except KeyboardInterrupt:
		return None
	except:
		print("Expected server ip after -s, but got {0}".format(ttt_server_name))
		
	return start_mark, ttt_server_name


def play_game(start_mark):
	'''
	LOOPS UNTIL GAME IS DONE OR THE CLIENT QUITS
	recv a message from the server. The message can be any of the following:
		a message with the active game board and instructions for the client user.
		an end of game message.
		an error message.
	'''
	shared_queue = Queue()
	client_listener = Thread(target=get_user_response_thread,name='CLIENT_LISNTENER_THREAD',args=(shared_queue,),daemon=True)
	server_listener = Thread(target=get_server_response_thread,name='SERVER_LISNTENER_THREAD',args=(shared_queue,),daemon=True)
	client_listener.start()
	server_listener.start()
	
	mock_server_first_args_req = (SERVER_MARK, (TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE, "Attempting to connect to server"))

	last_server_request_type = TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE
	
	while client_listener.is_alive() and server_listener.is_alive():
		print ("Awaiting server or client response...")
		if shared_queue.qsize() == 0 and last_server_request_type == TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE:
			shared_queue.put(mock_server_first_args_req)


		response = shared_queue.get()

		if response[0] == CLIENT_MARK and last_server_request_type == TTT_PRTCL_EXPECTING_INT_RESPONSE:
			#valid reason to send
			send_single_digit_response(response[1], SERVER_ADDRESS)
			
		elif response[0] == SERVER_MARK:
			#we are getting a message from the server, print the message
			#TODO if we want to keep it nice and clear: 
			os.system("{command} Attempting to clear screen".format(command = 'cls' if os.name == 'nt' else 'clear'))
			print(response[1][1])
			last_server_request_type = response[1][0]
			
			if response[1][0] == TTT_PRTCL_TERMINATE:
				#print the server message
				print("Connection terminating, goodbye.")
				client_socket.close() 	#TODO: IS THIS VALID?
				return True
				
			elif response[1][0] == TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE:
				#send if the client goes first
				send_single_digit_response(start_mark, SERVER_ADDRESS)
				time.sleep(1)

def main(argv):
	'''
	Connect to server and starts the game.
	
	argv -- list with [-c] [-s serverIP]
	'''
	global SERVER_ADDRESS
	
	start_mark, ttt_server_name = parse_cmd_line_args(argv)
	
	SERVER_ADDRESS = (ttt_server_name, TTT_SERVER_PORT)
	
	#play the game
	try:
		play_game(start_mark)
	except:
		pass
		
	client_socket.close()
	print("Goodbye.")
	sys.exit(0)

if __name__ == '__main__':
	'''
	Call main() with the appropriately parsed command line argument list
	'''
	# read commandline arguments
	fullCmdArguments = sys.argv

	#get the argument parts
	argumentList = fullCmdArguments[1:]

	#send it to main
	main(argumentList)
