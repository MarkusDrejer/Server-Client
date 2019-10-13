import socket
from configparser import ConfigParser
import sched, time
import threading

configur = ConfigParser()
configur.read('opt.conf')
packets = configur.get('ServerSettings', 'PackageSize')


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# Bind the socket to the port
server_address = (IPAddr, 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

connectionCode = 'com-0: '
timeoutMsg = 'con-res 0xFE'

SynAck = False
res = -1
timeout = 4
packetsSecond = 0
s = sched.scheduler(time.time, time.sleep)

def do_something(sc):
    global packetsSecond
    packetsSecond = 0
    s.enter(1, 0, do_something, (s,))

def threadPacket(name):
    s.enter(1, 0, do_something, (s,))
    s.run()

while True:
    sock.settimeout(None)
    print('\nWaiting for a client')
    data, address = sock.recvfrom(4096)
    print('received {} bytes from {}'.format(len(data), address))
    print(data)

    if data == (connectionCode + IPAddr).encode():
        sent = sock.sendto((connectionCode + 'accept ' + IPAddr).encode(), address)
        print('sent {} bytes back to {}'.format(sent, address))
        data, address = sock.recvfrom(4096)

        # people can access from here.
        if data == (connectionCode + 'accept').encode():
            print(data)
            print('Established connection to Client')
            sock.sendto('Connection Established'.encode(), address)
            SynAck = True
            i = threading.Thread(target=threadPacket, args=(1,))
            i.start()
    else:
        sent = sock.sendto('Server connection denied'.encode(), address)
        print('sent {} bytes back to {}'.format(sent, address))
        print('Denied Client connection access')
        SynAck = False

    while SynAck:
        sock.settimeout(timeout)
        try:
            if packetsSecond < int(packets):
                print('\nWaiting for input...')
                data, address = sock.recvfrom(4096)
                packetsSecond += 1
                print('Packets this second:')
                print(packetsSecond)
                res += 1
                message = 'msg-%s %s' % (res, data)
                res += 1
                response = 'res-%s - I am server' % res
                print(message)
                sock.sendto(response.encode(), address)
            else:
                sock.sendto('Too many packages, please wait'.encode(), address)
        except socket.timeout:
            print('The Client timed out')
            sock.sendto(timeoutMsg.encode(), address)
            data, address = sock.recvfrom(4096)
            print(data)
            break
