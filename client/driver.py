import json
from render_util import *
from select import select
from socket_util import *

def driver_main(renderer, factory, s):
    print("I'm a driver!")

    background = load_sprite("driver_background.png", factory)
    renderer.render([background])
    tank_angle = 0

    # TODO add needle
    compass_needle = load_sprite("compass_needle.png", factory)
    compass_needle.x = 150
    compass_needle.y = 37

    running = True

    key_map = {sdl2.SDLK_w: "u1", sdl2.SDLK_s: "d1", sdl2.SDLK_i: "u2", sdl2.SDLK_k: "d2"}
    keys = {"u1": False, "d1": False, "u2": False, "d2": False}

    while running:

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

            if event.type == sdl2.SDL_KEYDOWN:
                keysym = event.key.keysym.sym
                if keysym in key_map.keys():
                    keys[key_map[keysym]] = True

            if event.type == sdl2.SDL_KEYUP:
                keysym = event.key.keysym.sym
                if keysym in key_map.keys():
                    keys[key_map[keysym]] = False

        ready_to_read, ready_to_write, in_error = select([s], [s], [], 0)

        for ready in ready_to_read:

            server_data = ready.recv(10240).decode("utf-8")

            decoded_server_data = decode_socket_data(server_data)


            for data in decoded_server_data:
                loaded_data = json.loads(data)
                if (loaded_data["type"] == "update"):
                    tank_angle = loaded_data["data"]["tank"]["angle"]
                    break

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        compass_needle.angle = -tank_angle
        render_sprites([compass_needle], renderer)

