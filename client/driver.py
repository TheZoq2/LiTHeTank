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

    socket_buffer = SocketBuffer()

    while running:

        keys_have_changed = False
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


        #Send an update message to the server
        if keys_have_changed:
            send_keys(ready_to_write[0], keys)

        for ready in ready_to_read:

            server_data = ready.recv(10240).decode("utf-8")
            socket_buffer.push_string(server_data)

            #decoded_server_data = decode_socket_data(server_data)
            decoded_server_data = socket_buffer.get_messages()


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

def send_keys(socket, keys):
    left_amount = 0;
    right_amount = 0;
    if keys["u1"]:
        left_amount = 1
    if keys["d1"]:
        left_amount = -1
    if keys["u2"]:
        right_amount = 1
    if keys["d2"]:
        right_amount = -1

    #Send a message about the current track state to the server
    msg = create_socket_msg(
            "track_state", 
            json.dumps({"left_amount": left_amount, "right_amount": right_amount}))
    send_msg_to_socket(socket, msg)
