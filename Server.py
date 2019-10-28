import socket
from configparser import ConfigParser
from datetime import datetime
import time
import threading

configur = ConfigParser()
configur.read('opt.conf')
packets = configur.get('ServerSettings', 'PackageSize')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

server_address = (IPAddr, 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

connectionCode = 'com-0: '
timeoutMsg = 'con-res 0xFE'
SynAck = False
res = 1
timeout = 4
packetsSecond = 0
clientRes = res - 1
clientTestData = ''

def threadPacket():
    global packetsSecond
    while True:
        packetsSecond = 0
        time.sleep(1)

def writeToFile(text):
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    f = open("log.txt", "a+")
    f.write(text + " Handshake with: " + IPAddr + " at " + timestampStr + "\n")
    f.close()

while True:
    SynAck = False
    sock.settimeout(None)
    print('\nWaiting for a client')
    data, address = sock.recvfrom(4096)
    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data == (connectionCode + IPAddr).encode():
        sent = sock.sendto((connectionCode + 'accept ' + IPAddr).encode(), address)
        print('sent {} bytes back to {}'.format(sent, address))
        data, address = sock.recvfrom(4096)
        if data == (connectionCode + 'accept').encode():
            print(data)
            print('Established connection to Client')
            sock.sendto('Connection Established'.encode(), address)
            SynAck = True

            writeToFile("Accepted")

            threading.Thread(target=threadPacket).start()
    else:
        sent = sock.sendto('Server connection denied'.encode(), address)
        print('sent {} bytes back to {}'.format(sent, address))
        print('Denied Client connection access')

        writeToFile("Failed")

        SynAck = False

    while SynAck:
        sock.settimeout(timeout)
        try:
            if packetsSecond < int(packets):
                print('\nWaiting for input...')
                data, address = sock.recvfrom(4096)
                clientTestData = 'msg-%s' % clientRes
                if data.startswith(clientTestData.encode()) or data.startswith('con-h '.encode()):
                    clientTestData = 'msg-%s - disconnect' % clientRes
                    if data == clientTestData.encode():
                        print("Client closed the connection")
                        break
                    else:
                        packetsSecond += 1
                        print('Packets this second:')
                        print(packetsSecond)
                        print(data)
                        response = 'res-%s - I am server' % res
                        clientRes += 2
                        res += 2
                        sock.sendto(response.encode(), address)
                else:
                    sock.sendto('Something went wrong'.encode(), address)
            else:
                sock.sendto('Too many packages, please wait'.encode(), address)
                time.sleep(1)
        except socket.timeout:
            print('The Client timed out')
            sock.sendto(timeoutMsg.encode(), address)
            data, address = sock.recvfrom(4096)
            print(data)
            break
