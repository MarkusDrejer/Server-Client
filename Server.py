import socket
from configparser import ConfigParser
import sched, time
import threading
import sys

configur = ConfigParser()
configur.read('opt.conf')
packets = configur.get('ServerSettings', 'PackageSize')

packetsSecond = 0
connectionCode = 'com-0: '
timeoutMsg = 'con-res 0xFE'
timeout = 4
s = sched.scheduler(time.time, time.sleep)


def start_server():
    hostname = socket.gethostbyname(socket.gethostname())
    port = 10000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((hostname, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    sock.listen(2)

    while True:
        print('\nWaiting for a client')
        newConnection, address = sock.accept()
        try:
            threading.Thread(target=threadClient, args=(newConnection, hostname)).start()
        except:
            print("Thread did not start.")
            sock.close()


def threadClient(newConnection, hostname):
    data, address = newConnection.recvfrom(4096)
    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data == (connectionCode + hostname).encode():
        sent = newConnection.send((connectionCode + 'accept ' + hostname).encode())
        print('sent {} bytes back to {}'.format(sent, address))
        data, address = newConnection.recvfrom(4096)
        if data == (connectionCode + 'accept').encode():
            print(data)
            print('Established connection to Client')
            newConnection.send('Connection Established'.encode())
            messageHandling(newConnection)
    else:
        sent = newConnection.send('Server connection denied'.encode())
        print('sent {} bytes back to {}'.format(sent, address))
        print('Denied Client connection access')
        newConnection.close()


def messageHandling(newConnection):
    res = -1
    global packetsSecond
    threading.Thread(target=threadPacket).start()
    while True:
        newConnection.settimeout(timeout)
        try:
            if packetsSecond < int(packets):
                print('\nWaiting for input...')
                data, address = newConnection.recvfrom(4096)
                if data == 'disconnect'.encode():
                    newConnection.close()
                    print("This client closed the connection")
                    break
                else:
                    packetsSecond += 1
                    print('Packets from client this second:')
                    print(packetsSecond)
                    res += 1
                    message = 'msg-%s %s' % (res, data)
                    res += 1
                    response = 'res-%s - I am server' % res
                    print(message)
                    newConnection.send(response.encode())
            else:
                newConnection.send('Too many packages, please wait'.encode())
                time.sleep(1)
        except socket.timeout:
            print('The Client timed out')
            newConnection.send(timeoutMsg.encode())
            data, address = newConnection.recvfrom(4096)
            print(data)
            newConnection.close()
            break

def do_something():
    global packetsSecond
    packetsSecond = 0
    s.enter(1, 0, do_something)

def threadPacket():
    s.enter(1, 0, do_something)
    s.run()

if __name__ == "__main__":
   start_server()
