#!/usr/bin/env python3

import random
import socket
from vec import *
import json
from enum import Enum

PORT = 2000

class Tank:
    def  __init__(self):
        self.gun_angle = 0
        self.health = 100
        self.position = Vec2(0,0)
        self.angle = 0

        self.left_track = 0
        self.right_track = 0

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def update():
        forward_speed = left_track + right_track;


class Role(Enum):
    COMMANDER = 0,
    GUNNER = 1,
    DRIVER = 2,

def role_to_string(role):
    if role == Role.COMMANDER:
        return "COMMANDER"
    if role == Role.GUNNER:
        return "GUNNER"
    if role == Role.DRIVER:
        return "DRIVER"

role_list = [Role.COMMANDER, Role.GUNNER, Role.DRIVER]



class Client():
    def __init__(self, socket):
        self.socket = socket
        self.role = None

    def set_role(self, role):
        self.role = role

    def send_role(self):
        self.socket.send(bytes('{"role":"' + role_to_string(self.role) + '"}', 'utf-8'))


def distribute_roles(clients):
    if len(clients) == role_list:
        random.shuffle(role_list[:])

        for client in clients:
            client.set_role(role_list.pop())
            client.send_role()

        return clients
    else:
        return (None, "You need {} players to play".format(len(role_list)))


def main():
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind(("", PORT))
    # become a server socket
    serversocket.listen(5)

    print("Listening on port {}".format(PORT))

    clients = []

    tank = Tank()

    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        clientsocket.send(bytes(str(tank.to_json()), 'utf-8'))
        
        clients.append(Client(clientsocket))

        if len(clients) == len(role_list):
            clients = distribute_roles(clients)
            print(clients)


main()
