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
    compass_needle_medium = load_sprite("compass_needle_medium.png", factory)
    compass_needle.x = 223
    compass_needle.y = 41
    compass_needle_medium.x = 130
    compass_needle_medium.y = 116

    gun_angle = 0
    tank_angle = 0

    running = True

    socket_buffer = SocketBuffer()

    while running:

        key_is_pressed = False
        new_turn_dir = 0

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_k:
                    new_turn_dir = 1
                    key_is_pressed = True
                elif event.key.keysym.sym == sdl2.SDLK_j:
                    new_turn_dir = -1
                    key_is_pressed = True
            if event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym == sdl2.SDLK_k:
                    key_is_pressed = True
                elif event.key.keysym.sym == sdl2.SDLK_j:
                    key_is_pressed = True


        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        ready_to_read, ready_to_write, in_error = select([s], [s], [], 0)


        if key_is_pressed:
            msg = create_socket_msg("turn_state", json.dumps({"direction": new_turn_dir}))
            send_msg_to_socket(ready_to_write[0], msg)

        for ready in ready_to_write:
            send_msg_to_socket(ready, create_socket_msg("update", ""))

        for ready in ready_to_read:


            server_data = ready.recv(102400).decode("utf-8")

            socket_buffer.push_string(server_data);


            #decoded_server_data = decode_socket_data(server_data)
            decoded_server_data = socket_buffer.get_messages()
            for data in decoded_server_data:
                (type, loaded_data) = decode_socket_json_msg(data)
                if type == "update":
                    tank = loaded_data["tank"]
                    gun_angle = tank["gun_angle"] / math.pi * 180
                    tank_angle = tank["angle"] / math.pi * 180


            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        compass_needle.angle = -gun_angle - 90
        compass_needle_medium.angle = -tank_angle - 90
        render_sprites([background, compass_needle, compass_needle_medium], renderer)
        sdl2.render.SDL_RenderPresent(renderer.sdlrenderer)
