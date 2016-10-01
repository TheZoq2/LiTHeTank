from render_util import *

def driver_main(spriterenderer, factory, socket):
    print("I'm a driver!")

    compass = factory.from_image(RESOURCES.get_path("tank bot.png"))

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

            decoded_server_data = decode_server_data(server_data)

            tank_angle = 0

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

        compass.angle = -tank_angle
        spriterenderer.render([compass])

