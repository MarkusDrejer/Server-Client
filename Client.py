import socket
import time
import threading
import sys
from configparser import ConfigParser

configur = ConfigParser()
configur.read('opt.conf')
heartBeat = configur.get('ServerSettings', 'KeepAlive')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostbyname(socket.gethostname())
port = 10000

connectionCode = 'com-0: '
connected = False
heartBeatIntervalCheck = 0

def main():
    global connected
    global heartBeatIntervalCheck

    try:
        sock.connect((hostname, port))
    except:
        print("Connection Error")
        sys.exit()

    try:
        print('Sending IP for Syn')
        sock.send((connectionCode + hostname).encode())

        print('waiting for Syn/Ack')
        data, address = sock.recvfrom(4096)
        print('received {!r}'.format(data))

        if data == (connectionCode + 'accept ' + hostname).encode():
            print('Sending accept to server')
            sock.send((connectionCode + 'accept').encode())
            data, address = sock.recvfrom(4096)
            print(data)
            if data == 'Connection Established'.encode():
                connected = True
                threading.Thread(target=threadx).start()
                threading.Thread(target=threadBeat).start()

        message = ''
        while connected and message != 'disconnect':
            message = input()
            sock.send(message.encode())
            heartBeatIntervalCheck = 0

    finally:
        print('closing socket')
        connected = False
        sock.close()


def threadBeat():
    global heartBeatIntervalCheck

    while heartBeat == "True" and connected:
        if heartBeatIntervalCheck == 3:
            sock.send('con-h 0x00'.encode())
            heartBeatIntervalCheck = 0
        else:
            time.sleep(1)
            heartBeatIntervalCheck += 1

def threadx():
    global connected

    try:
        while connected:
            data, address = sock.recvfrom(4096)
            if(data == "con-res 0xFE".encode()):
                sock.send('con-res 0xFF'.encode())
                print("YOU GOT FUCKED. timed out")
                connected = False
            else:
                print(data)
    except:
        print("Listening thread closed")

if __name__ == "__main__":
   main()