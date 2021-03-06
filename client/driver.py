import json
import math
from render_util import *
from select import select
from socket_util import *

LEVER_1_X = 22
LEVER_2_X = 240
LEVER_NEUTRAL_Y = 73
LEVER_UP_Y = 26
LEVER_DOWN_Y = 80

def render_lever(x, sprites, direction, renderer):
    y = LEVER_NEUTRAL_Y
    sprite = sprites["neutral"]

    if direction > 0:
        y = LEVER_UP_Y
        sprite = sprites["up"]
    elif direction < 0:
        y = LEVER_DOWN_Y
        sprite = sprites["down"]

    sprite.x = x
    sprite.y = y
    render_sprites([sprite], renderer)


def lever_dir(up_key, down_key):
    direction = 0
    if up_key:
        direction += 1
    if down_key:
        direction -= 1
    return direction


def driver_main(renderer, factory, s):
    print("I'm a driver!")

    background = load_sprite("driver_background.png", factory)
    background.center = False
    tank_angle = 0
    gun_angle = 0

    # TODO add needle
    compass_needle = load_sprite("compass_needle.png", factory)
    compass_needle.x = 150
    compass_needle.y = 37
    compass_needle.center = False

    compass_needle_small = load_sprite("compass_needle_small.png", factory)
    compass_needle_small.x = 225
    compass_needle_small.y = 135
    compass_needle_small.center = False

    score_sprite = render_text("score: 0", factory)
    score_sprite.x = 320 // 2 - score_sprite.size[0] // 2
    score_sprite.y = 2
    score_sprite.center = False
    score = 0

    levers = {}
    levers["up"] = load_sprite("lever_up.png", factory)
    levers["down"] = load_sprite("lever_down.png", factory)
    levers["neutral"] = load_sprite("lever_neutral.png", factory)

    for lever in levers:
        levers[lever].center = False

    running = True

    key_map = {sdl2.SDLK_w: "u1", sdl2.SDLK_s: "d1", sdl2.SDLK_i: "u2", sdl2.SDLK_k: "d2"}
    keys = {"u1": False, "d1": False, "u2": False, "d2": False}

    socket_buffer = SocketBuffer()


    keys_have_changed = False
    while running:

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

            if event.type == sdl2.SDL_KEYDOWN:
                keysym = event.key.keysym.sym
                if keysym in key_map.keys():
                    keys_have_changed = True
                    keys[key_map[keysym]] = True

            if event.type == sdl2.SDL_KEYUP:
                keysym = event.key.keysym.sym
                if keysym in key_map.keys():
                    keys_have_changed = True
                    keys[key_map[keysym]] = False



        ready_to_read, ready_to_write, in_error = select([s], [s], [], 0)




        for ready in ready_to_write:
            send_msg_to_socket(ready, create_socket_msg("update", ""))
            #Send an update message to the server
            if keys_have_changed:
                send_keys(ready, keys)

        for ready in ready_to_read:

            server_data = ready.recv(10240).decode("utf-8")
            socket_buffer.push_string(server_data)

            #decoded_server_data = decode_socket_data(server_data)
            decoded_server_data = socket_buffer.get_messages()


            for data in decoded_server_data:
                type, loaded_data = decode_socket_json_msg(data)
                if (type == "update"):
                    tank_angle = loaded_data["tank"]["angle"] / math.pi * 180
                    gun_angle = loaded_data["tank"]["gun_angle"] / math.pi * 180

                    score = loaded_data["score"]
                    score_sprite = render_text("score: " + str(score), factory)
                    score_sprite.x = 320 // 2 - score_sprite.size[0] // 2
                    score_sprite.y = 2
                    score_sprite.center = False

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False


        compass_needle.angle = -tank_angle - 90
        compass_needle_small.angle = -gun_angle - 90

        render_sprites([background, compass_needle, compass_needle_small, score_sprite], renderer)

        render_lever(LEVER_1_X, levers, lever_dir(keys["u1"], keys["d1"]), renderer)
        render_lever(LEVER_2_X, levers, lever_dir(keys["u2"], keys["d2"]), renderer)

        sdl2.render.SDL_RenderPresent(renderer.sdlrenderer)

def send_keys(socket, keys):
    left_amount = 0
    right_amount = 0
    if keys["u2"]:
        left_amount = 1
    if keys["d2"]:
        left_amount = -1
    if keys["u1"]:
        right_amount = 1
    if keys["d1"]:
        right_amount = -1

    #Send a message about the current track state to the server
    msg = create_socket_msg(
            "track_state",
            json.dumps({"left_amount": left_amount, "right_amount": right_amount}))
    send_msg_to_socket(socket, msg)
