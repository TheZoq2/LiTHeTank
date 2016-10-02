#!/usr/bin/env python3
import socket
import sys
from select import select
import json
import math
import sdl2
import sdl2.ext
from socket_util import *
import render_util as ru
from gunner import *
from commander import *
from driver import *

WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(150, 255, 120)

def create_message_template(type, payload):
    return json.dumps({"type": type, "data": payload},)

def request_data_from_server(socket):
    #create_message_template(type)
    pass

def create_window():
    sdl2.ext.init()
    window_size = (1280, 720)
    window = sdl2.ext.Window("LiTHe Tank", size=window_size)
    renderer = sdl2.ext.Renderer(window)
    renderer.scale = (4, 4)
    window.show()

    factory = sdl2.ext.SpriteFactory(renderer=renderer)

    spriterenderer = factory.create_sprite_render_system(window)
    return window, spriterenderer, factory

def run():
    server_url =  "localhost"
    if len(sys.argv) == 2:
        server_url = sys.argv[1]

    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect((server_url, 2000))
    s.setblocking(False)

    window, renderer, factory = create_window()
    background = ru.create_rect(GREEN, (320, 180), factory)

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        ready_to_read, ready_to_write, in_error = select([s], [s], [], 0)

        for ready in ready_to_read:
            server_data = ready.recv(10240).decode("utf-8")

            decoded_server_data = decode_socket_data(server_data)

            for data in decoded_server_data:
                (type, decoded_data) = decode_socket_json_msg(data)
                if (type == "role"):
                    window, renderer, factory = create_window()
                    if (decoded_data["role"] == "GUNNER"):
                        gunner_main(renderer, factory, s)
                    if (decoded_data["role"] == "DRIVER"):
                        driver_main(renderer, factory, s)
                    if (decoded_data["role"] == "COMMANDER"):
                        commander_main(renderer, factory, s)

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        render_sprites([background], renderer)
        sdl2.render.SDL_RenderPresent(renderer.sdlrenderer)

    s.shutdown(socket.SHUT_WR)
    s.close()
    return 0



if __name__ == "__main__":
    sys.exit(run())
