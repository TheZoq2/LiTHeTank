#!/usr/bin/env python3
import socket
import sys
from select import select
import sdl2
import sdl2.ext
import json

WHITE = sdl2.ext.Color(255, 255, 255)

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)

def create_message_template(type, payload):
    return json.dumps({"type": type, "data": payload},)

def request_data_from_server(socket):
    #create_message_template(type)
    pass

def run():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("localhost", 2000))
    s.setblocking(False)

    sdl2.ext.init()
    window = sdl2.ext.Window("LiTHe Spank", size=(800, 600))
    window.show()

    world = sdl2.ext.World()

    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

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

        world.process()

    s.shutdown(socket.SHUT_WR)
    s.close()
    return 0

def decode_server_data(server_data):
    data_chunks = []
    while (server_data):
        index = server_data.find('{')
        bytes_to_read = int(server_data[0:index])
        server_data = server_data[index:]
        data_chunks.append(server_data[0:bytes_to_read])
        server_data = server_data[bytes_to_read:]
    return data_chunks


if __name__ == "__main__":
    sys.exit(run())
