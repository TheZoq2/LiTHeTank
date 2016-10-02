import sdl2

import json
import vec

import render_util as ru
from select import select
from socket_util import *
import pdb
import math

WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(150, 255, 120)

def commander_main(renderer, factory, socket):
    print("I'm a commander!")

    #background = load_sprite("driver_background.png", factory)
    #renderer.render([background])
    tank_angle = 0

    # TODO add needle
    tank_top_sprite = ru.load_sprite("tank top.png", factory)
    tank_bottom_sprite = ru.load_sprite("tank bot.png", factory)
    background = factory.from_color(GREEN, size=(320, 180))
    background.angle = 0

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

        enemies = []
        bullets = []

        for ready in ready_to_read:

            server_data = ready.recv(102400).decode("utf-8")

            decoded_server_data = decode_socket_data(server_data)

            tank_top_sprite.x = 200
            tank_top_sprite.y = 200

            for data in decoded_server_data:
                (type, loaded_data) = decode_socket_json_msg(data)
                if type == "update":
<<<<<<< HEAD
                    tank = loaded_data["tank"]
                    enemies = loaded_data["enemies"]
                    bullets = loaded_data["bullets"]
                    tank_top_sprite.x = tank["position"]["x"]
                    tank_top_sprite.y = tank["position"]["y"]
                    tank_top_sprite.angle = tank["gun_angle"]

                   # print("Got update msg with x {} y {}".format(tank["position"]["x"],tank["position"]["y"]))
=======
                    tank_data = loaded_data["tank"]
                    update_tank_sprite(tank_top_sprite, tank_bottom_sprite, tank_data)


>>>>>>> 23958aef7c5e219742599b92c8633b44cdd5562e

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

<<<<<<< HEAD
        _render_enemies(enemies, renderer, factory)
        _render_bullets(bullets, renderer, factory)
        ru.render_sprites([tank_top_sprite], renderer)


def _render_enemies(enemies, renderer, factory):
    sprites = []
    for enemy in enemies:
        enemy_sprite = ru.load_sprite("enemy.png", factory)
        enemy_sprite.x = int(enemy["position"]["x"])
        enemy_sprite.y = int(enemy["position"]["y"])
        enemy_sprite.angle = vec.radians_to_degrees(enemy["angle"])
        #enemy_sprite.size = enemy["size"]
        sprites.append(enemy_sprite)

    ru.render_sprites(sprites, renderer)
        

def _render_bullets(bullets, renderer, factory):
    sprites = []
    for bullet in bullets:
        bullet_sprite = ru.load_sprite("bullet_normal.png", factory)
        bullet_sprite.x = int(bullet["position"]["x"])
        bullet_sprite.y = int(bullet["position"]["y"])
        bullet_sprite.angle = vec.radians_to_degrees(
            vec.Vec2(bullet["velocity"]["x"], bullet["velocity"]["y"]).angle())
        sprites.append(bullet_sprite)

    ru.render_sprites(sprites, renderer)

=======
        ru.render_sprites([background, tank_bottom_sprite, tank_top_sprite], renderer)



def update_tank_sprite(tank_top_sprite, tank_bottom_sprite, tank_data):
    x = round(tank_data["position"]["x"])
    y = round(tank_data["position"]["y"])
    tank_bottom_sprite.x = x
    tank_bottom_sprite.y = y
    tank_top_sprite.x = x
    tank_top_sprite.y = y
    #tank_top_sprite.angle = tank["gun_angle"]
    tank_bottom_sprite.angle = tank_data["angle"] / math.pi * 180
    tank_top_sprite.angle = tank_data["gun_angle"] / math.pi * 180
>>>>>>> 23958aef7c5e219742599b92c8633b44cdd5562e
