import socket
from configparser import ConfigParser
import sched, time
import threading
import sys
import traceback

configur = ConfigParser()
configur.read('opt.conf')
packets = configur.get('ServerSettings', 'PackageSize')

connectionCode = 'com-0: '
timeoutMsg = 'con-res 0xFE'
timeout = 4
s = sched.scheduler(time.time, time.sleep)

def main():
   start_server()

def start_server():
    hostname = socket.gethostbyname(socket.gethostname())

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    try:
        sock.bind((hostname, 10000))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    sock.listen(2)

    while True:
        connection, address = sock.accept()
        try:
            threading.Thread(target=threadClient, args=(connection, hostname)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()
            sock.close()

def do_something(sc):
    global packetsSecond
    packetsSecond = 0
    s.enter(1, 0, do_something, (s,))

def threadPacket(name):
    s.enter(1, 0, do_something, (s,))
    s.run()

def threadClient(sock, hostname):
    print('\nWaiting for a client')
    data, address = sock.recvfrom(4096)
    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data == (connectionCode + hostname).encode():
        sent = sock.send((connectionCode + 'accept ' + hostname).encode())
        print('sent {} bytes back to {}'.format(sent, address))
        data, address = sock.recvfrom(4096)
        if data == (connectionCode + 'accept').encode():
            print(data)
            print('Established connection to Client')
            sock.send('Connection Established'.encode())
            messageHandling(sock)
    else:
        sent = sock.send('Server connection denied'.encode())
        print('sent {} bytes back to {}'.format(sent, address))
        print('Denied Client connection access')


def messageHandling(newClient):
    res = -1
    packetsSecond = 0
    i = threading.Thread(target=threadPacket, args=(1,))
    i.start()
    while True:
        newClient.settimeout(timeout)
        try:
            if packetsSecond < int(packets):
                print('\nWaiting for input...')
                data, address = newClient.recvfrom(4096)
                packetsSecond += 1
                print('Total packets from client:')
                print(packetsSecond)
                res += 1
                message = 'msg-%s %s' % (res, data)
                res += 1
                response = 'res-%s - I am server' % res
                print(message)
                newClient.send(response.encode())
            else:
                newClient.send('Too many packages, please wait'.encode())
        except socket.timeout:
            print('The Client timed out')
            newClient.send(timeoutMsg.encode())
            data, address = newClient.recvfrom(4096)
            print(data)
            break

if __name__ == "__main__":
   main()
