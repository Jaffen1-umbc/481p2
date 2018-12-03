from _thread import *
from sched import *
import time, sys
from select import *
from socket import *
from traceback import *
ACTIVE_GAMES_IN_USE_MUTEX = False
ACTIVE_GAMES = []
server_input = None
client_input = None
client_socket = socket(AF_INET, SOCK_DGRAM)
TTT_SERVER_PORT = 13037
SERVER_ADDRESS = ('', TTT_SERVER_PORT)





#clear function
def clear():
	#try printing a bunch of stuff to clear screen
	try:
		print( chr(27) + "[2J" )
		#cls for windows, clear for linux/mac osx
		_ = call('cls' if os.name == 'nt' else 'clear')
	except:
		print("INPUT TIMEOUT")
		

	
def get_user_or_server_io():
	'''
	Gets user response while ignoring all incoming messages. This is so that when
	we dont get a backlock of server responses.
	'''
	global client_input
	
	server_response = None
	client_input = None
	client_socket.settimeout(0)
	timer = Timer(0, clear)
	start_new_thread(start_timer_if_client_input, (timer))
	start_new_thread(get_single_digit_response, (message))
	while server_response == None and client_input == None:
		server_response = recv_server_response()
	
	client_socket.settimeout(None) #blocking mode
	timer.cancel()

def get_single_digit_response(message):
	'''
	Propmpts user with message, and gets a single digit from user input.
	RETURNS:
		<unsigned int> -- a single digit.
	'''
	user_input = "default_invalid"

	#validate user input
	timer = Timer(TTT_PRTCL_TIMEOUT, clear)
	timer.start()
	while not user_input.isdigit()
		#prompt user with message
		user_input = input(message)
	try:
		client_input = int(user_input[0])
		timer.cancel()
		return int(user_input[0])
	except:
		print("ERROR @ TTTC.py::get_single_digit_response(): FAILED TO INTERPRET USER INPUT... TRYING AGAIN")
		client_input = None
		user_input = "default_invalid"
#		return get_single_digit_response(message)


def checkVals():
	if user_input is not None or server_input is not None:
		print(user_input, server_input)

what if we flushed socket before sending 
def main2():
	global user_input
	global server_input
	client_socket.settimeout(0.0)
	while True:
		input = select([sys.stdin, client_socket], [], [], 1)
		print(input)
		if input:
			value = sys.stdin.readline().rstrip()
			server_input = None
			if value.isdigit():
				print (value)
				sys.exit(0)
			else:
				print ("invalid input")
		else:
			print("poop")
	
def game_watcher_thread():
	'''
	Periodically call each games pass_client_message so that if a message wasnt 
	recived by the client, or a message needs to be sent and hasnt been, it 
	will be sent again.
	'''
	global ACTIVE_GAMES
	global ACTIVE_GAMES_IN_USE_MUTEX
	a = 0
	while a <3 :
		print_stack()
		#acquire lock
		while ACTIVE_GAMES_IN_USE_MUTEX:
				pass
		ACTIVE_GAMES_IN_USE_MUTEX = True
	
		print(ACTIVE_GAMES)
			#game.pass_client_message(None)
	
		#release lock
		ACTIVE_GAMES_IN_USE_MUTEX = False 
		a += 1
		time.sleep(0.5)
		
		
def main():
	'''
		main function. Receives messages and starts a thread to figure out what to 
		do with them.
	''' 
	print ('The server is ready to receive connections')
	try:
		a = 0
		watcher = start_new_thread(game_watcher_thread, ())
		while 1:
			print("main thread: ", time.ctime(time.time()), "\n", watcher.get_ident())
			print_stack()
			time.sleep(1)
	except KeyboardInterrupt:
		#dont crash program... allow for cleanup
		print("\nCLOSING DOWN TIC-TAC-TOE SERVER")
		print_exc()
		sys.exit(0)
		
if __name__ == '__main__':
	main2()
	
"""



s = scheduler(time.time, time.sleep)
s.enter(10, 1, 
def periodic(scheduler, interval, action, actionargs=()):
	scheduler.enter(interval, 1, periodic,
					(scheduler, interval, action, actionargs))
"""
