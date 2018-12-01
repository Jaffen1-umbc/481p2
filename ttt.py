#################################################################
#	Tic-Tac-Toe Protocol Module				#
#	import this to create your own server or client.	#
#	usage: import ttt					#
#	Noah Jaffe						#
#	TCP Socket Programming					#
#	CMSC 481						#
#	11/05/2018						#
#################################################################

import struct

#CONSTANTS & GLOBALS
TTT_SERVER_PORT = 13037
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
TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE = 4 #4 is the size of a packed '!I' value


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
	conn.sendto(struct.pack('!I', len(message)), addr)	
	#SEND: MESSAGE
	conn.sendto(message.encode(), addr)	
	#pack expecting response val '!I'
	#SEND PACKED: EXPECTING RESPONSE VAL
	conn.sendto(struct.pack('!I', expecting_response_val), addr)	

def RECIEVING_FROM_SERVER_TO_CLIENT(conn):
	'''
	Receives the size of the next incoming response, and the next incoming response.
	RECIEVING FROM SERVER TO CLIENT: 
		RECV PACKED: MESSAGE RESPONSE LENGTH
		unpack '!I' and .recv that many bytes
		RECV: MESSAGE
		RECV PACKED: EXPECTING RESPONSE VAL
		unpack '!i' and add to ret_list
	
	ARGUMENTS:
		conn -- the connection

	RETURNS:
		server_response -- the response received.
		[<EXPECTING RESPONSE>, <MESSAGE>]
		<EXPECTING RESPONSE> Valid values are <unsigned int>:
			TTT_PRTCL_TERMINATE
				-- connection will be closing, message is the last message from the server.
			TTT_PRTCL_EXPECTING_NO_RESPONSE
				-- expecting no response, message is just a message.
			TTT_PRTCL_EXPECTING_INT_RESPONSE
				-- expecting a single digit integer response, message is a prompt for the user
			TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE
				-- expecting the TTT_PRTCL_REQUEST_FIRST_ARGS response, message is instructions.
		<MESSAGE> Valid values are <string>:
			A string with a message.
	'''
	ret_list = []
	#recv a message length from the server
	server_msg_len_buf = RECIEVE_BYES(conn, TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
	if not server_msg_len_buf:
		return None
	server_msg_len, = struct.unpack("!I", server_msg_len_buf)
	
	#recv a message from the server	
	server_msg = RECIEVE_BYES(conn, server_msg_len).decode()
	ret_list.append(server_msg) 

	#recv an int value of the expexted response value
	expecting_response_buf = RECIEVE_BYES(conn, TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
	if not expecting_response_buf:
		return None
	expecting_response, = struct.unpack("!I", expecting_response_buf)
	#add expcted response value to list	
	try:
		ret_list.insert(0, expecting_response)
	except:
		#if insertion failed bc of some reason or expecting response is None, then default to termination
		ret_list.insert(0, TTT_PRTCL_TERMINATE)

	return ret_list
	

def SENDING_FROM_CLIENT_TO_SERVER():
	'''
	Sends an unsigned int value to the server
	
	SENDING FROM CLIENT TO SERVER:
		pack single digit val '!I'
		SEND PACKED: SINGLE DIGIT VAL
	
	'''
	client_socket.send(struct.pack('!I', num))
	

def RECIEVING_FROM_CLIENT_TO_SERVER(conn):
	'''
	Recv's one message from the client:
	1. <unsigned int> a response value (packed)

	RECIEVING FROM CLIENT TO SERVER:
		RECV PACKED: SINGLE DIGIT VAL
		unpack '!I'

	ARGUMENTS:
		conn -- the connection

	RETURNS:
		<unsigned int> -- a single digit value
		None -- if there was en error reading the response
	'''
	#recv message header
	digit_buff = RECIEVE_BYES(conn, TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
	#receive bytes of data for the packed unsigned int from client
	try:
		val,  = struct.unpack('!I', digit_buff)
		return val
	except:
		print ("ERROR @ ttts.py::get_client_response(): RECV RESPONSE OF NONE")
	return None

def RECIEVE_BYES(conn, size):
	'''
	Receives messages of a specific size (size) from the connection (conn)

	ARGUMENTS:
		conn -- the connection
		size -- number of bytes to read

	RETURNS:
		<bytes> -- the (packed/encoded) message from the client
		None -- if connection failed before reading in the message
	'''
	#recv message header
	encoded_msg = b''
	while size:
		temp = conn.recv(size)
		if not temp:
			return None
		encoded_msg += temp
		size -= len(temp)

	return encoded_msg
