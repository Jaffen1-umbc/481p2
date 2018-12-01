# Math Client
import struct
import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Get user input (This should have validation)
    op, a, b = input(">").split()
    a = int(a)
    b = int(b)
    op = op.encode('ascii')

    # Pack the data and send it to the server
    binary = struct.pack(">3sii", op, a, b)
    udp_socket.sendto(binary, ("localhost", 5000))

    # Receive and print the result if successful
    binary = udp_socket.recv(512)
    success, result = struct.unpack(">bi", binary)
    if success == 1:
        print("Result:",result)
    else:
        print("Unable to complete calculation")
