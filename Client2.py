import socket
import time
import threading
from configparser import ConfigParser

configur = ConfigParser()
configur.read('opt.conf')
heartBeat = configur.get('ServerSettings', 'KeepAlive')

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

connectionCode = 'com-0: '
connected = False
timeoutAck = 'con-res 0xFF'
heartBeatmsg = 'con-h 0x00'

def threadBeat(name):
    while(heartBeat == 'True'):
        time.sleep(3)
        sock.send(heartBeatmsg.encode())

def threadx(name):
    global connected

    while(True):
        data, address = sock.recvfrom(4096)
        if(data == "con-res 0xFE".encode()):
            sock.send(timeoutAck.encode())
            print("YOU GOT FUCKED. timed out")
            connected = False
            break
        else:
            print(data)


try:
    # Send data
    sock.connect((IPAddr, 10000))
    print('Sending IP for Syn')
    sock.send((connectionCode + IPAddr).encode())

    # Receive response
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
            x = threading.Thread(target=threadx, args=(1,))
            x.start()
            y = threading.Thread(target=threadBeat, args=(1,))
            y.start()

    while connected:
            sock.send(input().encode())


finally:
    print('closing socket')
    sock.close()
