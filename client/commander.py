import sdl2

import json
import vec

import render_util as ru
from select import select
from socket_util import *
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
import pdb
import math
import time

WHITE = sdl2.ext.Color(255, 255, 255)
GREEN = sdl2.ext.Color(150, 255, 120)

HEALTH_GREEN = sdl2.ext.Color(0, 255, 0)

HEALTH_BAR_OFFSET = 20
TANK_HEALTH_OFFSET = 8

RED = sdl2.ext.Color(255, 0, 0)
HEALTH_BAR_HEIGHT = 2
HEALTH_BAR_WIDTH = 16

SCROLL_BORDER = 50

def render_tile(x, y, tiles, renderer, cam_pos):
    index = (x + y) % len(tiles)
    tiles[index].x = x * 64
    tiles[index].y = y * 64
    ru.render_sprites([tiles[index]], renderer, cam_pos = cam_pos)

def commander_main(renderer, factory, socket):
    print("I'm a commander!")

    camera_position = vec.Vec2(0, 0)

    # TODO add needle
    tank_top_sprite = ru.load_sprite("tank top.png", factory)
    tank_bottom_sprite = ru.load_sprite("tank bot.png", factory)
    enemy_sprite = ru.load_sprite("enemy1_body.png", factory)
    enemy_turret_sprite  = ru.load_sprite("enemy1_turret.png", factory)
    bullet_sprite = ru.load_sprite("bullet_normal.png", factory)
    bullet_sprite.scale = (0.1, 0.1)

    tiles = [ru.load_sprite("tile" + str(i + 1) + ".png", factory) for i in range(4)]

    running = True

    socket_buffer = SocketBuffer()

    enemies = []
    bullets = []

    needs_update = True
    last_update = time.time()

    tank_health_red = ru.create_rect(RED, (HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), factory)
    tank_health_green = ru.create_rect(HEALTH_GREEN,
                                       (HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), factory)
    tank_health_red.center = False
    tank_health_green.center = False

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
                    update_tank_sprite(tank_top_sprite, tank_bottom_sprite, 
                                       tank_data, tank_health_red, tank_health_green)

            if not server_data:
                print("Server disconnected")
                running = False

            if server_data == b"exit":
                running = False

        tank_pos = vec.Vec2(tank_bottom_sprite.x, tank_bottom_sprite.y)
        if tank_pos.x - camera_position.x < SCROLL_BORDER:
            camera_position.x -= 1
        elif tank_pos.x - camera_position.x > SCREEN_WIDTH - SCROLL_BORDER:
            camera_position.x += 1
        if tank_pos.y - camera_position.y < SCROLL_BORDER:
            camera_position.y -= 1
        elif tank_pos.y - camera_position.y > SCREEN_HEIGHT - SCROLL_BORDER:
            camera_position.y += 1

        tile_size = tiles[0].size[0]
        for x in range(SCREEN_WIDTH // tile_size + 2):
            for y in range(SCREEN_HEIGHT // tile_size + 3):
                tile_x = camera_position.x // tile_size + x
                tile_y = camera_position.y // tile_size + y
                render_tile(tile_x, tile_y, tiles, renderer, camera_position)

        ru.render_sprites([tank_bottom_sprite, tank_top_sprite, 
                           tank_health_red, tank_health_green], renderer, camera_position)
        _render_enemies(enemies, renderer, enemy_sprite,
                        enemy_turret_sprite, camera_position, factory)
        _render_bullets(bullets, renderer, bullet_sprite, camera_position)
        sdl2.render.SDL_RenderPresent(renderer.sdlrenderer)


def _render_enemies(enemies, renderer, enemy_sprite, enemy_turret_sprite, cam_pos, factory):
    for enemy in enemies:
        health_red = ru.create_rect(RED, (HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), factory)
        health_green = ru.create_rect(HEALTH_GREEN,
                                      (int(HEALTH_BAR_WIDTH *
                                       (enemy["health"] / enemy["original_health"])),
                                                    HEALTH_BAR_HEIGHT), factory)
        health_red.center = False
        health_green.center = False

        x = int(enemy["position"]["x"])
        y = int(enemy["position"]["y"])
        health_red.x = x
        health_red.y = y - HEALTH_BAR_OFFSET
        health_green.x = x
        health_green.y = y - HEALTH_BAR_OFFSET
        enemy_sprite.x = x
        enemy_sprite.y = y
        enemy_turret_sprite.x = x
        enemy_turret_sprite.y = y
        enemy_sprite.angle = vec.radians_to_degrees(enemy["angle"])
        enemy_turret_sprite.angle = vec.radians_to_degrees(enemy["turret_angle"])
        ru.render_sprites([enemy_sprite, enemy_turret_sprite, health_red, health_green],
                          renderer, cam_pos)


def _render_bullets(bullets, renderer, bullet_sprite, cam_pos):
    for bullet in bullets:
        bullet_sprite.x = int(bullet["position"]["x"])
        bullet_sprite.y = int(bullet["position"]["y"])
        bullet_sprite.angle = vec.radians_to_degrees(
            vec.Vec2(bullet["velocity"]["x"], bullet["velocity"]["y"]).angle())
        ru.render_sprites([bullet_sprite], renderer, cam_pos = cam_pos)


def update_tank_sprite(tank_top_sprite, tank_bottom_sprite, 
                       tank_data, health_red, health_green):
    x = round(tank_data["position"]["x"])
    y = round(tank_data["position"]["y"])
    health_red.x = x - TANK_HEALTH_OFFSET
    health_red.y = y - HEALTH_BAR_OFFSET
    health_green.x = x - TANK_HEALTH_OFFSET
    health_green.y = y - HEALTH_BAR_OFFSET
    health_green.scale = ((tank_data["health"] / tank_data["original_health"]),
                          1)
    
    tank_bottom_sprite.x = x
    tank_bottom_sprite.y = y
    tank_top_sprite.x = x
    tank_top_sprite.y = y
    #tank_top_sprite.angle = tank["gun_angle"]
    tank_bottom_sprite.angle = tank_data["angle"] / math.pi * 180
    tank_top_sprite.angle = tank_data["gun_angle"] / math.pi * 180


