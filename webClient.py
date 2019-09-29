import socket

def Main():
    host = '216.93.167.81'
    port = 80

    mySocket = socket.socket()
    mySocket.connect((host, port))

    mySocket.send("GET /website-medical-website-design-services HTTP/1.1\r\nHost:physicianwebpages.com\r\n\r\n".encode())
    data = mySocket.recv(10000).decode()
    print(data)
    mySocket.close()

Main()