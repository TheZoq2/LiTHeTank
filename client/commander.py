import sdl2

import json

import render_util as ru
from select import select
from socket_util import *
import pdb
import math

WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(150, 255, 120)

def commander_main(renderer, factory, socket):
    print("I'm a commander!")

    #background = load_sprite("driver_background.png", factory)
    #renderer.render([background])
    tank_angle = 0

    # TODO add needle
    tank_top_sprite = ru.load_sprite("tank top.png", factory)
    background = factory.from_color(GREEN, size=(320, 180))
    background.angle = 0

    running = True

    while running:

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        ready_to_read, ready_to_write, in_error = select([socket], [socket], [], 0)

        #ready_to_write[0].send_msg_to_socket()
        send_msg_to_socket(ready_to_write[0], create_socket_msg("update", ""))


        for ready in ready_to_read:

            server_data = ready.recv(102400).decode("utf-8")

            decoded_server_data = decode_socket_data(server_data)

            tank_top_sprite.x = 200
            tank_top_sprite.y = 200

            for data in decoded_server_data:
                (type, loaded_data) = decode_socket_json_msg(data)
                if type == "update":
                    tank = loaded_data["tank"]
                    tank_top_sprite.x = round(tank["position"]["x"])
                    tank_top_sprite.y = round(tank["position"]["y"])
                    #tank_top_sprite.angle = tank["gun_angle"]
                    tank_top_sprite.angle = tank["angle"] / math.pi * 180

                   #print("Got update msg with x {} y {}".format(tank["position"]["x"],tank["position"]["y"]))

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        ru.render_sprites([background, tank_top_sprite], renderer)


