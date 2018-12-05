#################################################################
#   Tic-Tac-Toe UDP Protocol Module                             #
#   import this to create your own server or client.            #
#   usage: import ttt                                           #
#   Noah Jaffe                                                  #
#   UDP Socket Programming                                      #
#   CMSC 481                                                    #
#   12/05/2018                                                  #
#################################################################

import struct

#TTT SPECIFIC CONSTANTS & GLOBALS
SERVER_FIRST = 0
SERVER_MARK = 1
CLIENT_MARK = 2
UNUSED_MARK = 0
CATS_GAME = -1

TTT_PRTCL_REQUEST_FIRST_ARGS = "Please send an unsigned int representing if the client wishes to make the first move.\n\t0 -- sever should go first\n\t1 -- client should go first"
TTT_PRTCL_GOT_FIRST_ARGS_ERR = "Failed to receive proper game initiation arguments. Terminating connection.\nNext time " + TTT_PRTCL_REQUEST_FIRST_ARGS
TTT_PRTCL_INSTRUCTIONS = "Welcome to Tic Tac Toe!\nEnter [0-8] for the position of your move, or 9 to quit:\n0|1|2\n-----\n3|4|5\n-----\n6|7|8\n"
TTT_PRTCL_INVALID_CLIENT_INPUT = "Invalid input, try again."
TTT_PRTCL_REQUEST_CLIENT_TURN = " | | \n-----\n | | \n-----\n | | \nEnter [0-8] for the position of your move, or 9 to quit:\n"
TTT_PRTCL_CLIENT_ERR = "Sorry, that was invalid input. Please try again."

TTT_PRTCL_TERMINATE = 0
TTT_PRTCL_EXPECTING_NO_RESPONSE = 1
TTT_PRTCL_EXPECTING_INT_RESPONSE = 2
TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE = 3

TTT_PRTCL_TIMEOUT = 5 #5 sec of timeout between resends
TTT_PRTCL_MAX_TIMEOUT = 600 #if over X sec of no communication, we assume they quit

TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE = 37 #37 is the size of a packed '!I' value with the address attached

TTT_SERVER_PORT = 13037

#TO CREATE A SOCKET: (binded socket must be nonblocking)
SOCK = socket(AF_INET, SOCK_DGRAM)
SOCK.setblocking(False)
SERVER_ADDRESS = ('', TTT_SERVER_PORT)

def SENDING_FROM_SERVER_TO_CLIENT(addr, expecting_response_val, message):
	'''
	Sends three messages to the client.
	1. <int> a message length (packed)
	2. <string> the message (encoded)
	3. <int> an expected response value (packed)
	
	SENDING FROM SERVER TO CLIENT:
		pack message response length '!I'
		SEND PACKED: MESSAGE RESPONSE LENGTH
		SEND: MESSAGE
		pack expecting response val '!I'
		SEND PACKED: EXPECTING RESPONSE VAL

	ARGUMENTS:
		addr -- the connection address
		expecting_response_val -- the response expected from the client
		message -- a message to send to the client

	'''
	#pack message response length '!I'
	#SEND PACKED: MESSAGE RESPONSE LENGTH
	encoded = message.encode()
	SOCK.sendto(struct.pack('!I', sys.getsizeof(encoded)), addr) #send size of 37
	#SEND: MESSAGE
	SOCK.sendto(encoded, addr) #send variable size
	#pack expecting response val '!I'
	#SEND PACKED: EXPECTING RESPONSE VAL
	SOCK.sendto(struct.pack('!I', expecting_response_val), addr) #send size of 37	


def RECV_MSG_FROM_SERVER():
	'''
	RECIEVING FROM SERVER TO CLIENT: 
		RECV PACKED: MESSAGE RESPONSE LENGTH
		unpack '!I' and that many bytes
		RECV: MESSAGE
		RECV PACKED: EXPECTING RESPONSE VAL
		unpack '!i' and add to ret_list
	Receives the size of the next incoming response, and the next incoming response.

	RETURNS:
		None -- if there was no response or only part of a response
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
		server_msg_len_buf = SOCK.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE) #get size of 37
		if not server_msg_len_buf:
			return None
		server_msg_len, = struct.unpack("!I", server_msg_len_buf[0])
	
		#print("Recving msg of len: ", server_msg_len) #TODO DEBUG  
	
		#recv a message from the server	
		server_msg = SOCK.recvfrom(int(server_msg_len)) #get the variable sized message
		ret_list.append(server_msg[0].decode())

		#print("Recved msg: ", server_msg[0])	#TODO DEBUG
	
		#recv an int value of the expexted response value
		expecting_response_buf = SOCK.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE) #get size of 37
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
    

def SEND_MSG_TO_SERVER(num, addr):
	'''
	Sends an unsigned int value to the server
	
	SENDING FROM CLIENT TO SERVER:
		pack single digit val '!I'
		SEND PACKED: SINGLE DIGIT VAL
	
	'''
	SOCK.sendto(struct.pack('!I', num), addr)
	
    
def RECV_MSG_FROM_CLIENT():
	'''
	Recv's one message from the client:
	1. <unsigned int> a response value (packed)

	RECEIEVING FROM CLIENT TO SERVER:
		RECV PACKED: SINGLE DIGIT VAL
		unpack '!I'

	ARGUMENTS:
		addr -- the address receive from

	RETURNS:
		<unsigned int> -- a single digit value
		None -- if there was en error reading the response
	'''
	#receive bytes of data for the packed unsigned int from client
	try:
		digit_buff = SOCK.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
		val, = struct.unpack('!I', digit_buff[0])
		return val, digit_buff[1]
	except:
		pass
		#print ("ERROR @ ttts.py::get_client_response(): RECV INVALID CLIENT MESSAGE:\n{0}".format(None))
	return None, None
