#!/usr/bin/env python3
import socket
import sys
from select import select
import json
import math
import sdl2
import sdl2.ext
from socket_util import *

WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(150, 255, 120)

RESOURCES = sdl2.ext.Resources(__file__, "resources")

def create_message_template(type, payload):
    return json.dumps({"type": type, "data": payload},)

def request_data_from_server(socket):
    #create_message_template(type)
    pass

yolo = 0
def run():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("localhost", 2000))
    s.setblocking(False)

    sdl2.ext.init()
    window_size = (1200, 700)
    window = sdl2.ext.Window("LiTHe Spank", size=window_size)
    renderer = sdl2.ext.Renderer(window)
    renderer.scale = (4, 4)
    window.show()

    factory = sdl2.ext.SpriteFactory(renderer=renderer)
    turret = factory.from_image(RESOURCES.get_path("tank top.png"))
    tank = factory.from_image(RESOURCES.get_path("tank bot.png"))
    background = factory.from_color(GREEN, size=window_size)

    spriterenderer = factory.create_sprite_render_system(window)

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

            decode_server_data(server_data)

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        global yolo
        yolo += 1
        tank.y = int(50 * math.sin(yolo / 300)) + 80
        turret.y = int(50 * math.sin(yolo / 300)) + 80
        spriterenderer.render([background, tank, turret])

    s.shutdown(socket.SHUT_WR)
    s.close()
    return 0



if __name__ == "__main__":
    sys.exit(run())
