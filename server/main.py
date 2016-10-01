#!/bin/python

import socket;

PORT = 2000

def main():
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind(("", PORT))
    # become a server socket
    serversocket.listen(5)

    print("Listening on port {}".format(PORT))

    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        clientsocket.send(b"HEEEEEEJ")

main()
