import socket
import time
import threading
from configparser import ConfigParser

configur = ConfigParser()
configur.read('opt.conf')
heartBeat = configur.get('ServerSettings', 'KeepAlive')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

connectionCode = 'com-0: '
connected = False
timeoutAck = 'con-res 0xFF'
heartBeatmsg = 'con-h 0x00'
inputCheck = 0

def threadBeat():
    global inputCheck

    while heartBeat == "True":
        if inputCheck == 3:
            sock.send(heartBeatmsg.encode())
            inputCheck = 0
        else:
            time.sleep(1)
            inputCheck += 1

def threadx():
    global connected

    while True:
        data, address = sock.recvfrom(4096)
        if(data == "con-res 0xFE".encode()):
            sock.send(timeoutAck.encode())
            print("YOU GOT FUCKED. timed out")
            connected = False
            break
        else:
            print(data)

try:
    sock.connect((IPAddr, 10000))
    print('Sending IP for Syn')
    sock.send((connectionCode + IPAddr).encode())

    print('waiting for Syn/Ack')
    data, address = sock.recvfrom(4096)
    print('received {!r}'.format(data))

    if data == (connectionCode + 'accept ' + IPAddr).encode():
        print('Sending accept to server')
        sock.send((connectionCode + 'accept').encode())
        data, address = sock.recvfrom(4096)
        print(data)
        if data == 'Connection Established'.encode():
            connected = True
            threading.Thread(target=threadx).start()
            threading.Thread(target=threadBeat).start()

    while connected:
        sock.send(input().encode())
        inputCheck = 0


finally:
    print('closing socket')
    sock.close()
