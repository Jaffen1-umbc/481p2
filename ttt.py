#################################################################
#   Tic-Tac-Toe UDP Protocol Module                             #
#   import this to create your own server or client.            #
#   usage: import ttt                                           #
#   Noah Jaffe                                                  #
#   UDP Socket Programming                                      #
#   CMSC 481                                                    #
#   12/05/2018                                                  #
#################################################################

import socket #.sendto, .recvfrom 
from struct import pack as ttt_pack
from struct import unpack as ttt_unpack
from sys import getsizeof as ttt_msg_size

#TTT_FIRST_ARGS
_TTT_SERVER_FIRST_	=	0
_TTT_CLIENT_FIRST_	=	1

#TTT_EXPECTING_RESPONSE_VALS
_TTT_PRTCL_TERMINATE_						=	9
_TTT_PRTCL_EXPECTING_NO_RESPONSE_			=	1
_TTT_PRTCL_EXPECTING_INT_RESPONSE_			=	2
_TTT_PRTCL_EXPECTING_FIRST_ARGS_RESPONSE_	=	3

#TTT_TIMEOUT_VALS
#seconds of timeout between server resends
_TTT_PRTCL_TIMEOUT_		=	5 
#seconds of no communication until server assumes client quit
_TTT_PRTCL_MAX_TIMEOUT_	=	600

#TTT_SEND_RECV_SIZE
#the size of a packed '!I' value with the address attached
_TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE_ = 37

#TTT_SOCKET
_TTT_SERVER_PORT_ = 13037

#TTT_PRTCL_STRINGS
_TTT_PRTCL_REQUEST_FIRST_ARGS_ = "Please send an unsigned int representing if the client wishes to make the first move.\n\t0 -- sever should go first\n\t1 -- client should go first"
_TTT_PRTCL_GOT_FIRST_ARGS_ERR_ = "Failed to receive proper game initiation arguments. Terminating connection.\nNext time " + _TTT_PRTCL_REQUEST_FIRST_ARGS_
_TTT_PRTCL_INSTRUCTIONS_ = "Welcome to Tic Tac Toe!\nEnter [0-8] for the position of your move, or 9 to quit:\n0|1|2\n-----\n3|4|5\n-----\n6|7|8\n"
_TTT_PRTCL_INVALID_CLIENT_INPUT_ = "Invalid input, try again."
_TTT_PRTCL_REQUEST_CLIENT_TURN_ = " | | \n-----\n | | \n-----\n | | \nEnter [0-8] for the position of your move, or 9 to quit:\n"
_TTT_PRTCL_CLIENT_ERR_ = "Sorry, that was invalid input. Please try again."


def ttt_init_server_socket(server_ip):
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.setblocking(False)
	sock.bind((server_ip, _TTT_SERVER_PORT_))
	return sock

def ttt_init_client_socket():
	return socket(AF_INET, SOCK_DGRAM)

def ttt_get_server_address(server_ip):
	return (server_ip, _TTT_SERVER_PORT_)

def ttt_send_server_msg_to_client(sock, message, expecting_response_val, client_address):
	#1. SEND the packed ('!I') encoded message length 
	sock.sendto(ttt_pack('!I', ttt_msg_size(message.encode())), client_address)
	#2. SEND the encoded message  					
	sock.sendto(message.encode(), client_address)
	#3. SEND the packed ('!I') expecting response value
	sock.sendto(ttt_pack('!I', expecting_response_val), client_address)
	

def ttt_recv_server_msg_from_client(sock):
	'''
	Gets an incoming message to a TTT server, or None if there is nothing incoming. 
	RETURNS:
		<unsignd int>, <sender's address> -- unsigned int value from the client, and the client's address
		OR:
		None, None -- if no message in the socket queue.
	'''
	#1. RECV a packed ('!I') value (and the sender's address) 
	try:
		message_tuple = sock.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
		message, = ttt_unpack('!I', message_tuple[0])
		return message, message_tuple[1]
	except:
		pass
	
	return None, None
	
	

def ttt_recv_client_msg_from_server(sock):
	'''
	*Notes:
	Due to the server being a non-blocking datagram
	socket, it is possible for the <socket>.recvfrom() 
	function to return None. When the function returns 
	None for any of the steps for a client receiving 
	from the server, it is reccomended to go back to 
	step 1, and repeat until all 3 steps are completed 
	successfully.
	
	RETURNS:
		[<expecting_response_val>, <message>] -- the expecting response value, and the message from the server
		OR 
		None -- if there was no, or an incomplete response from the server
		
		
	'''
	ret_list = []
	
	try:
	
		#1. RECV the packed ('!I') encoded message length
		message_len_tuple = sock.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
		message_len, = ttt_unpack('!I', message_len_tuple[0])
	
		#2. RECV the encoded message
		message_tuple = sock.recvfrom(message_len)
		message = message_tuple[0].decode()
		ret_list.append(message)
		
		#3. RECV the packed ('!I') expecting response value
		expecting_response_val_tuple = sock.recvfrom(TTT_PRTCL_PACKED_UNSIGNED_INT_SIZE)
		expecting_response_val, = ttt_unpack('!I', expecting_response_val_tuple[0])
		ret_list.insert(0, expecting_response_val)
		
		return ret_list
		
	except:
		pass
	
	return None #incomplete message, so none to receive
	

def ttt_send_client_msg_to_server(sock, message, server_address):
	'''
	ARGUMENTS:
		sock -- the socket to use
		message -- the message to send
			message valid types are: unsigned int 
		server_address -- the TTT server address
		
	RETURNS:
		True -- valid message to send
		False -- invalid message
	'''
	try:
		#1. SEND a packed ('!I') value
		sock.sendto(ttt_pack('!I', message), server_address)
	except:
		return False
	return True
	
