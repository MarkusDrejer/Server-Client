import socket

# GET / HTTP/1.1\r\nHost:physicianwebpages.com\r\n\r\n
def main():
    host = "216.93.167.81"
    port = 80

    mySocket = socket.socket()
    mySocket.connect((host, port))

    mySocket.send("GET /about.html / HTTP/1.1\r\nHost:physicianwebpages.com\r\n\r\n".encode())
    data = mySocket.recv(10000000).decode()

    print(data)

    mySocket.close

main()