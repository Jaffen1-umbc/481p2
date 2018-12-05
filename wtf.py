import threading, queue, time, sys, select

SERVER_MARK = 1
CLIENT_MARK = 2

def get_user_response_thread(shared_queue):
	'''
	Thread that gets user input and if it is valid, it will put it into the queue.
	'''
	print("wi")
	try:
		while shared_queue.qsize() == 0:
			i, o, e = select.select([sys.stdin],[],[], 0.0001)
			for s in i:
				if s == sys.stdin:
					client_input = sys.stdin.readline()
					#CHECK VALID USER INPUT HERE
					try:
						print(">>", client_input)
						temp = int(client_input[0])
						shared_queue.put_nowait((CLIENT_MARK, temp))
					except:
						pass
	except:
		raise KeyboardInterrupt

def x(shared_queue):
	try:
		while shared_queue.qsize() == 0:
			print("<<<")
			time.sleep(1)
	except:
		raise KeyboardInterrupt
#	shared_queue.put((SERVER_MARK, (1,"butt")))
	

q = queue.Queue()
t1 = threading.Thread(target=get_user_response_thread,name="poop",args=(q,),daemon=True)
t2 = threading.Thread(target=x,name="poop2",args=(q,),daemon=True)
t1.start()
t2.start()
print(vars(t1), threading.active_count())

while t1.is_alive() and t2.is_alive():
	print (q.qsize())
	time.sleep(1)
