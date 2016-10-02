import sdl2

import json
import vec

import render_util as ru
from select import select
from socket_util import *
import pdb
import math
import time

WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(150, 255, 120)
RED = sdl2.ext.Color(255, 0, 0)
HEALTH_BAR_HEIGHT = 4
HEALTH_BAR_WIDTH = 16

def commander_main(renderer, factory, socket):
    print("I'm a commander!")

    #background = load_sprite("driver_background.png", factory)
    #renderer.render([background])
    tank_angle = 0

    # TODO add needle
    tank_top_sprite = ru.load_sprite("tank top.png", factory)
    tank_bottom_sprite = ru.load_sprite("tank bot.png", factory)
    enemy_sprite = ru.load_sprite("enemy1_body.png", factory)
    enemy_turret_sprite  = ru.load_sprite("enemy1_turret.png", factory)
    bullet_sprite = ru.load_sprite("bullet_normal.png", factory)
    bullet_sprite.scale = (0.1, 0.1)
    background = ru.create_rect(GREEN, (320, 180), factory)

    running = True

    socket_buffer = SocketBuffer()

    enemies = []
    bullets = []

    needs_update = True
    last_update = time.time()

    while running:

        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        ready_to_read, ready_to_write, in_error = select([socket], [socket], [], 0)

        if needs_update == True or (time.time() - last_update) > 0.1:
            for ready in ready_to_write:
                send_msg_to_socket(ready, create_socket_msg("update", ""))
                needs_update = False
                last_update = time.time()
                #print("Requesting update")

        for ready in ready_to_read:
            server_data = ready.recv(4096).decode("utf-8")
            socket_buffer.push_string(server_data)

            #decoded_server_data = decode_socket_data(server_data)
            decoded_server_data = socket_buffer.get_messages()

            for data in decoded_server_data:
                (type, loaded_data) = decode_socket_json_msg(data)
                if type == "update":
                    needs_update = True
                    tank_data = loaded_data["tank"]
                    enemies = loaded_data["enemies"]
                    bullets = loaded_data["bullets"]
                    update_tank_sprite(tank_top_sprite, tank_bottom_sprite, tank_data)

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        ru.render_sprites([background, tank_bottom_sprite, tank_top_sprite], renderer)
        _render_enemies(enemies, renderer, enemy_sprite, enemy_turret_sprite)
        _render_bullets(bullets, renderer, bullet_sprite)
        sdl2.render.SDL_RenderPresent(renderer.sdlrenderer)


def _render_enemies(enemies, renderer, enemy_sprite, enemy_turret_sprite):
    for enemy in enemies:
        health_red = ru.create_rect(RED, (HEALTH_BAR_HEIGHT, HEALTH_BAR_WIDTH))
        health_green = ru.create_rect(GREEN, (HEALTH_BAR_HEIGHT, 
                               HEALTH_BAR_WIDTH * enemy["health"]))
        health_red.center = False
        health_green.center = False
        
        x = int(enemy["position"]["x"])
        y = int(enemy["position"]["y"])
        enemy_sprite.x = x
        enemy_sprite.y = y
        enemy_turret_sprite.x = x
        enemy_turret_sprite.y = y
        enemy_sprite.angle = vec.radians_to_degrees(enemy["angle"])
        enemy_turret_sprite.angle = vec.radians_to_degrees(enemy["turret_angle"])
        ru.render_sprites([enemy_sprite, enemy_turret_sprite], renderer)


def _render_bullets(bullets, renderer, bullet_sprite):
    for bullet in bullets:
        bullet_sprite.x = int(bullet["position"]["x"])
        bullet_sprite.y = int(bullet["position"]["y"])
        bullet_sprite.angle = vec.radians_to_degrees(
            vec.Vec2(bullet["velocity"]["x"], bullet["velocity"]["y"]).angle())
        ru.render_sprites([bullet_sprite], renderer)


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
