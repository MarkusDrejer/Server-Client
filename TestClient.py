import socket
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
server_address = (IPAddr, 10000)

while True:
    sock.sendto(input().encode(), server_address)
    data, address = sock.recvfrom(4096)
    print(data)