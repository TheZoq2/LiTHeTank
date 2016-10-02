import sdl2.ext
from vec import Vec2, vec2_from_direction
import math
import random
import json
import pdb

FIRE_LEFT = 0
FIRE_RIGHT = 1

DEFAULT_ENEMY_SIZE = 5
DEFAULT_BULLET_DAMAGE = 10
DEFAULT_BULLET_SPEED = 150
DEFAULT_ENEMY_HEALTH = 20
SPAWN_FREQUENCY = 1
TANK_SIZE = 16
MAXIMUM_SPAWN_DISTANCE = 100
ENEMY_SPEED = 100

# The default probability for the enemies. Higher numbers result in lower frequencies
DEFAULT_FIRING_FREQUENCY = 10


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
        self.tank = tank
        self.enemies = []
        self.bullets = []

    def update(self, delta_time):
        if self.tank.firing_left:
            self._fire_tank(FIRE_LEFT)
            self.tank.firing_left = False
        elif self.tank.firing_right:
            self._fire_tank(FIRE_RIGHT)
            self.firing_right = False
        self._update_bullet_positions(delta_time)
        self._update_enemy_positions(delta_time)
        self._fire_enemies(delta_time)
        self._remove_dead_enemies()
        self._spawn_enemies(delta_time)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def _fire_tank(self, cannon):
        # TODO differentiate between left and right
        total_angle = self.tank.gun_angle + self.tank.angle
        self.bullets.append(Bullet(
            self.tank.position + vec2_from_direction(total_angle, TANK_SIZE + 3), 
                                  total_angle))
    
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
            if not bullet.position.is_within_bounds(self.tank.position, 100):
                bullets_to_remove.append(bullet)
        self.bullets = [bullet for bullet in self.bullets if bullet not in bullets_to_remove]

    def _update_enemy_positions(self, delta_time):
        for enemy in self.enemies:
            enemy.angle = -enemy.position.relative_angle_to(self.tank.position)
            enemy.position += vec2_from_direction(enemy.angle, ENEMY_SPEED * delta_time)
    
    def _remove_dead_enemies(self):
        self.enemies = [e for e in self.enemies if not e.is_dead()]

    def _fire_enemies(self, delta_time):
        for enemy in self.enemies:
            should_fire = not random.randint(0, int(enemy.firing_frequency * (1 / delta_time)))

            # if the random number was 0, fire
            if should_fire:
                self._enemy_fire(enemy)
                
    def _enemy_fire(self, enemy):
        self.bullets.append(Bullet(
            enemy.position + vec2_from_direction(enemy.angle, enemy.size + 3), enemy.angle))
    
    def _spawn_enemies(self, delta_time):
        if len(self.enemies) < 5:
            if random.randint(0, int(SPAWN_FREQUENCY / delta_time)) == 0:
                randx = self.tank.position.x + \
                        random.randint(-MAXIMUM_SPAWN_DISTANCE, MAXIMUM_SPAWN_DISTANCE)
                randy = self.tank.position.y + \
                        random.randint(-MAXIMUM_SPAWN_DISTANCE, MAXIMUM_SPAWN_DISTANCE)
                self.enemies.append(Enemy(Vec2(randx, randy)))
        

