import socket
import time
import threading
from configparser import ConfigParser

configur = ConfigParser()
configur.read('opt.conf')
heartBeat = configur.get('ServerSettings', 'KeepAlive')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
server_address = (IPAddr, 10000)


connectionCode = 'com-0: '
connected = False
heartBeatIntervalCheck = 0

def threadBeat():
    global heartBeatIntervalCheck

    while heartBeat == "True" and connected:
        if heartBeatIntervalCheck == 3:
            sock.sendto('con-h 0x00'.encode(), address)
            heartBeatIntervalCheck = 0
        else:
            time.sleep(1)
            heartBeatIntervalCheck += 1

def threadx():
    global connected

    while(True):
        data, address = sock.recvfrom(4096)
        if(data == "con-res 0xFE".encode()):
            sock.sendto('con-res 0xFF'.encode(), server_address)
            print("YOU GOT FUCKED. timed out")
            connected = False
            break
        else:
            print(data)


try:
    # Send data
    print('Sending IP for Syn')
    sock.sendto((connectionCode + IPAddr).encode(), server_address)

    # Receive response
    print('waiting for Syn/Ack')
    data, address = sock.recvfrom(4096)
    print('received {!r}'.format(data))

    if data == (connectionCode + 'accept ' + IPAddr).encode():
        print('Sending accept to server')
        sock.sendto((connectionCode + 'accept').encode(), server_address)
        data, address = sock.recvfrom(4096)
        print(data)
        if data == 'Connection Established'.encode():
            connected = True
            threading.Thread(target=threadx).start()
            threading.Thread(target=threadBeat).start()

    message = ''
    while connected and message != 'disconnect':
        message = input()
        sock.sendto(message.encode(), address)
        heartBeatIntervalCheck = 0


finally:
    print('closing socket')
    sock.close()