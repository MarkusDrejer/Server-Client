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
res = 0

def threadBeat():
    global heartBeatIntervalCheck
    global res
    while heartBeat == "True" and connected:
        if heartBeatIntervalCheck == 3:
            sock.sendto('con-h 0x00'.encode(), address)
            res += 2
            heartBeatIntervalCheck = 0
        else:
            time.sleep(1)
            heartBeatIntervalCheck += 1

def threadx():
    global connected
    try:
        while(connected):
            data, address = sock.recvfrom(4096)
            if(data == "con-res 0xFE".encode()):
                sock.sendto('con-res 0xFF'.encode(), server_address)
                print("YOU GOT FUCKED. timed out")
                connected = False
                break
            else:
                if data.startswith("res-".encode()):
                    print(data)
                elif data == 'Something went wrong'.encode():
                    print(data)
    except:
        print("Listening thread closed")

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

    messageCode = ''
    message = ''
    while connected and message != 'disconnect':
        message = input()
        messageCode = "msg-%s" % res
        sock.sendto((messageCode + ' ' + message).encode(), address)
        res += 2
        heartBeatIntervalCheck = 0

finally:
    print('closing socket')
    connected = False
    sock.close()