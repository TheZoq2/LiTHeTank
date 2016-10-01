import sdl2

import json

import render_util as ru
from select import select
from socket_util import *


def commander_main(renderer, factory, socket):
    print("I'm a driver!")

    #background = load_sprite("driver_background.png", factory)
    #renderer.render([background])
    tank_angle = 0

    # TODO add needle
    tank_sprite = ru.load_sprite("tank top.png", factory)

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

            server_data = ready.recv(10240).decode("utf-8")

            decoded_server_data = decode_server_data(server_data)


            for data in decoded_server_data:
                loaded_data = json.loads(data)
                if loaded_data["type"] == "update":
                    tank = loaded_data["data"]["tank"]
                    tank_sprite.x = 50
                    tank_sprite.y = 50

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        #compass.angle = -tank_angle
        ru.render_sprites([tank_sprite], renderer)


