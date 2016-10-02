import json
import math
import sdl2
import sdl2.ext
from render_util import *
from select import select
from socket_util import *

def gunner_main(renderer, factory, s):

    print("I'm a gunner!")

    background = load_sprite("gunner_background.png", factory)
    compass_needle = load_sprite("compass_needle.png", factory)
    compass_needle.x = 223
    compass_needle.y = 41
    gun_angle = 0

    running = True

    while running:

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_k:
                    send_msg_to_socket(ready_to_write[0], create_socket_msg("rotate_gun_right", ""))
                elif event.key.keysym.sym == sdl2.SDLK_j:
                    send_msg_to_socket(ready_to_write[0], create_socket_msg("rotate_gun_left", ""))

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        ready_to_read, ready_to_write, in_error = select([s], [s], [], 0)

        send_msg_to_socket(ready_to_write[0], create_socket_msg("update", ""))

        for ready in ready_to_read:

            server_data = ready.recv(102400).decode("utf-8")

            decoded_server_data = decode_socket_data(server_data)

            for data in decoded_server_data:
                (type, loaded_data) = decode_socket_json_msg(data)
                if type == "update":
                    tank = loaded_data["tank"]
                    gun_angle = tank["gun_angle"]

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        compass_needle.angle = -gun_angle
        render_sprites([background, compass_needle], renderer)
