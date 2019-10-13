import socket
import time
import threading
from configparser import ConfigParser

# step 1: client 1 login successfully
# step 2: client 2 send IP, but no accept. Jumps over second IF statement

configur = ConfigParser()
configur.read('opt.conf')
heartBeat = configur.get('ServerSettings', 'KeepAlive')

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
server_address = (IPAddr, 10000)

connectionCode = 'com-0: '
connected = False
timeoutAck = 'con-res 0xFF'
heartBeatmsg = 'con-h 0x00'

def threadBeat(name):
    while(heartBeat == 'True'):
        time.sleep(3)
        sock.sendto(heartBeatmsg.encode(), server_address)

def threadx(name):
    global connected

    while(True):
        data, address = sock.recvfrom(4096)
        if(data == "con-res 0xFE".encode()):
            sock.sendto(timeoutAck.encode(), server_address)
            print("YOU GOT FUCKED. timed out")
            connected = False
            break
        else:
            print(data)


try:
    # Send data
    print('Sending IP for Syn')
    sock.sendto((connectionCode + IPAddr).encode(), server_address)


    # if True:
        # print('Sending accept to server')
        # sock.sendto((connectionCode + 'accept').encode(), server_address)
        # data, address = sock.recvfrom(4096)
        # print(data)
    if True:
        connected = True
        x = threading.Thread(target=threadx, args=(1,))
        x.start()
        y = threading.Thread(target=threadBeat, args=(1,))
        y.start()

    while True:
        sock.sendto(input().encode(), server_address)


finally:
    print('closing socket')
    sock.close()
