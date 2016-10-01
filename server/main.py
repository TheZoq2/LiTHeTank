#!/usr/bin/env python3

import random
import socket
from vec import *
import json
from enum import Enum
import select

PORT = 2000

class Tank:
    def  __init__(self):
        self.gun_angle = 0
        self.health = 100
        self.position = Vec2(0,0)
        self.angle = 0
        self.firing = False

        self.left_track = 0
        self.right_track = 0

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def update():
        add_speed = left_track + right_track
        add_angle = -left_track + right_track

        self.angle += add_angle
        self.position += vec2_from_direction(self.angle, add_speed)

    def set_track_state(self, left, right):
        self.left_track = left
        self.right_track = right

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


def get_client_msg(type, payload):
    return json.dumps({"type": type, "data": payload},)

def send_msg_to_client(socket, msg):
    final_msg = "{}{}".format(len(msg), msg)

    socket.send(bytes(final_msg, 'utf-8'))

class Client():
    def __init__(self, socket):
        self.socket = socket
        self.role = None

    def set_role(self, role):
        self.role = role

    def send_role(self):
        #self.socket.send(bytes('{"role":"' + role_to_string(self.role) + '"}', 'utf-8'))
        #self.socket.send(bytes(get_client_msg("role", role_to_string(self.role)), 'utf-8'))
        send_msg_to_client(self.socket, get_client_msg("role", role_to_string(self.role)))


def distribute_roles(clients):
    if len(clients) == len(role_list):
        random.shuffle(role_list[:])

        for client in clients:
            client.set_role(role_list.pop())
            client.send_role()

        return clients
    else:
        return (None, "You need {} players to play".format(len(role_list)))


def update_client(client):
    (ready_to_read, ready_to_write, in_error) = select.select(
                    [client.socket], 
                    [client.socket],
                    [],
                    0
                )
    for s in ready_to_read:
        data = s.recv(4096);


def run_game(clients):
    for client  in  clients:
        client.send_role()

    while True:
        #Check all the sockets
        pass

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
        clientsocket.setblocking(False)
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        #clientsocket.send(bytes(str(tank.to_json()), 'utf-8'))
        
        clients.append(Client(clientsocket))

        if len(clients) == len(role_list):
            clients = distribute_roles(clients)
            run_game(clients)
            #print(clients)


main()
