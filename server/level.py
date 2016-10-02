import sdl2.ext
import time
import time
from vec import Vec2, vec2_from_direction
import math
import random
import json
import pdb
from enum import Enum

FIRE_LEFT = 0
FIRE_RIGHT = 1

DEFAULT_ENEMY_SIZE = 16
DEFAULT_BULLET_DAMAGE = 10
DEFAULT_BULLET_SPEED = 150
DEFAULT_ENEMY_HEALTH = 20
SPAWN_FREQUENCY = 1
TANK_SIZE = 16
MAXIMUM_SPAWN_DISTANCE = 100
ENEMY_SPEED = 20
ENEMY_TURN_SPEED  = math.pi / 2
DESPAWN_RADIUS = 500

# The default probability for the enemies. Higher numbers result in lower frequencies
DEFAULT_FIRING_FREQUENCY = 3.5

HUNTING = 0,
SHOOTING = 1,


def turn_angle_to_angle(angle, target_angle, speed, threshold):
    angle_diff = target_angle - angle
    angle_diff = ((angle_diff + math.pi) % (math.pi * 2)) - math.pi
    if abs(angle_diff) > threshold:
        if angle_diff < 0:
            return (angle + speed, False)
        else:
            return (angle - speed, False)
    else:
        return (angle, True)


# class AirStrike():
# 
#     def __init__(self, target):
#         self.target = target
#         pos, velocity = None
# 
#     #def _generate


class Enemy():

    def __init__(self, position,
                 angle=None,
                 health=DEFAULT_ENEMY_HEALTH,
                 size=DEFAULT_ENEMY_SIZE,
                 firing_frequency=DEFAULT_FIRING_FREQUENCY):
        self.position = position
        self.angle = angle if angle is not None else 0
        self.health = health
        self.size = size
        self.firing_frequency = firing_frequency
        self.state = HUNTING
        self.turret_angle = 0
        self.last_shot = time.time()

    def is_dead(self):
        return self.health <= 0


class Bullet():

    def __init__(self, position, angle,
                 speed=DEFAULT_BULLET_SPEED,
                 damage=DEFAULT_BULLET_DAMAGE):
        self.position = position
        self.velocity = vec2_from_direction(angle, speed)
        self.damage = damage


class Level():

    def __init__(self, tank):
        self.air_strike = None
        self.tank = tank
        self.enemies = []
        self.bullets = []

    def update(self, delta_time):
        if self.tank.firing_left:
            self._fire_tank(FIRE_LEFT)
            self.tank.firing_left = False
        elif self.tank.firing_right:
            self._fire_tank(FIRE_RIGHT)
            self.tank.firing_right = False
        self._handle_bullet_collisions()
        self._update_bullet_positions(delta_time)
        self._update_enemy_positions(delta_time)
        self._fire_enemies(delta_time)
        self._remove_dead_enemies()
        self._spawn_enemies(delta_time)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def _fire_tank(self, cannon):
        # TODO differentiate between left and right
        if cannon == FIRE_LEFT:
            self.bullets.append(Bullet(
                self.tank.position + vec2_from_direction(
                    # Move the bullet slightly to the left 
                    self.tank.gun_angle - (math.pi/2), TANK_SIZE/2) + \
                    vec2_from_direction(self.tank.gun_angle, TANK_SIZE + 3),
                                      self.tank.gun_angle))
        else:
            self.bullets.append(Bullet(
                self.tank.position + vec2_from_direction(
                    # Move the bullet slightly to the right
                    self.tank.gun_angle + (math.pi/2), TANK_SIZE/2) + \
                    vec2_from_direction(self.tank.gun_angle, TANK_SIZE + 3),
                                      self.tank.gun_angle))


    def _handle_bullet_collisions(self):
        bullets_to_remove = []
        for bullet in self.bullets:
            if bullet.position.is_within_bounds(self.tank.position, TANK_SIZE):
                self.tank.health -= bullet.damage
                bullets_to_remove.append(bullet)
                print("TANK HIT")
                continue
            for enemy in self.enemies:
                if bullet.position.is_within_bounds(enemy.position, enemy.size):
                    enemy.health -= bullet.damage
                    self.bullets.remove(bullet)
                    bullets_to_remove.append(bullet)
                    print("ENEMY HIT")
        self.bullets = [bullet for bullet in self.bullets if bullet not in bullets_to_remove]

    def _update_bullet_positions(self, delta_time):
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.position += bullet.velocity * delta_time
            if not bullet.position.is_within_bounds(self.tank.position, DESPAWN_RADIUS):
                bullets_to_remove.append(bullet)
        self.bullets = [bullet for bullet in self.bullets if bullet not in bullets_to_remove]

    def _update_enemy_positions(self, delta_time):
        for enemy in self.enemies:
            shoot_range = (50, 100)

            enemy_to_tank = enemy.position - self.tank.position
            target_angle = enemy.position.relative_angle_to(self.tank.position)
            if enemy.state == HUNTING:
                #enemy.position += vec2_from_direction(enemy.angle, ENEMY_SPEED * delta_time)
                if abs(enemy_to_tank) > shoot_range[1] or abs(enemy_to_tank) < shoot_range[0]:
                    (enemy.angle, has_to_turn) = turn_angle_to_angle(
                                        enemy.angle, 
                                        target_angle, 
                                        ENEMY_TURN_SPEED * delta_time,
                                        math.pi / 6)

                    if abs(enemy_to_tank) > shoot_range[1]:
                        enemy.position += vec2_from_direction(enemy.angle, ENEMY_SPEED * delta_time)
                    else:
                        enemy.position -= vec2_from_direction(enemy.angle, ENEMY_SPEED * delta_time)
                else:
                    enemy.state = SHOOTING
            elif enemy.state == SHOOTING:
                if abs(enemy_to_tank) < shoot_range[0] or abs(enemy_to_tank) > shoot_range[1]:
                    enemy.state = HUNTING
                else:
                    (enemy.turret_angle, has_to_turn) = turn_angle_to_angle(
                                        enemy.turret_angle, 
                                        target_angle, 
                                        ENEMY_TURN_SPEED * delta_time,
                                        math.pi / 9)


    def _remove_dead_enemies(self):
        self.enemies = [e for e in self.enemies if not e.is_dead()]

    def _fire_enemies(self, delta_time):
        for enemy in self.enemies:
            #should_fire = not random.randint(0, int(enemy.firing_frequency * (1 / delta_time)))
            should_fire = (time.time() - enemy.last_shot) > enemy.firing_frequency

            # if the random number was 0, fire
            if should_fire:
                self._enemy_fire(enemy)
                enemy.last_shot = time.time()

    def _enemy_fire(self, enemy):
        self.bullets.append(Bullet(
            enemy.position + vec2_from_direction(enemy.turret_angle, enemy.size + 3), enemy.turret_angle))

    def _spawn_enemies(self, delta_time):
        if len(self.enemies) < 5:
            if random.randint(0, int(SPAWN_FREQUENCY / delta_time)) == 0:
                angle = (random.randint(0, 1000) / 1000) * math.pi * 2
                self.enemies.append(Enemy(self.tank.position + vec2_from_direction(angle, 100)))


