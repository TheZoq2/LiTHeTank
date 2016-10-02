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
TANK_SIZE = 14
MAXIMUM_SPAWN_DISTANCE = 100
ENEMY_SPEED = 10
ENEMY_TURN_SPEED = math.pi / 4
DESPAWN_RADIUS = 500
ENEMY_DESPAWN_RADIUS = 500
AIR_STRIKE_STARTING_DISTANCE = 200
AIR_STRIKE_SPEED = 30
AIR_STRIKE_FREQUENCY = 2
AIR_STRIKE_EXPLOSION_STRENGTH = 50
AIR_STRIKE_EXPLOSION_RADIUS = 30
AIR_STRIKE_BOMB_RESOLUTION = 4
AIR_STRIKE_BOMB_DAMAGE = 40
INTER_AIR_STRIKE_DISTANCE = 50

# Where the bombs should be dropped
AIR_STRIKES = [-1, 0, 1]

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


class AirStrike():

    def __init__(self, tank_position):
        self.target = tank_position
        pos, velocity = self._generate_start_position(tank_position)
        self.position = pos
        self.velocity = velocity
        # list of ints indicating how many multiples of air strike distance to drop each bomb
        self.bombs = AIR_STRIKES

    def _generate_start_position(self, tank_position):
        start_position = tank_position + \
                vec2_from_direction(random.randrange(0, 7), 
                                    AIR_STRIKE_STARTING_DISTANCE)
        velocity = vec2_from_direction(start_position.relative_angle_to(tank_position),
                                      AIR_STRIKE_SPEED)
        return start_position, velocity

    def should_drop_bomb(self):
        if not self.bombs:
            return False
        bomb = self.bombs[0]
        position_vector = vec2_from_direction(self.velocity.angle(), 
                                              bomb * INTER_AIR_STRIKE_DISTANCE)
        return position_vector.is_within_bounds(self.position, AIR_STRIKE_BOMB_RESOLUTION)

    def drop_bomb(self):
        """Removes one of the bombs from the list of bombs"""
        self.bombs = self.bombs[1:]
        

class Enemy():

    def __init__(self, position,
                 angle=None,
                 health=DEFAULT_ENEMY_HEALTH,
                 size=DEFAULT_ENEMY_SIZE,
                 firing_frequency=DEFAULT_FIRING_FREQUENCY):
        self.position = position
        self.angle = angle if angle is not None else 0
        self.health = health
        self.original_health = health
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
        self.score = 0
        self._spawn_an_enemy()
        self._spawn_an_enemy()
        self._spawn_an_enemy()

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
        self._update_air_strike_position(delta_time)
        self._fire_enemies(delta_time)
        self._remove_dead_enemies()
        self._spawn_enemies(delta_time)
        self._spawn_airstrike(delta_time)

    def _add_explosion(self, pos, strength):
        pass

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def _update_air_strike_position(self, delta_time):
        if self.air_strike is not None:
            self.air_strike.position += self.air_strike.velocity
            if self.air_strike.should_drop_bomb():
                self.air_strike.drop_bomb()
                self._damage_players_explosion(AIR_STRIKE_BOMB_DAMAGE,
                                               AIR_STRIKE_EXPLOSION_RADIUS,
                                               self.air_strike.position)
                self._add_explosion(self.air_strike.position, AIR_STRIKE_EXPLOSION_STRENGTH)
            if self.air_strike.position.distance_to(self.tank.position) > DESPAWN_RADIUS:
                self.air_strike = None

    def _damage_players_explosion(self, damage, radius, explosion_position):
        for enemy in self.enemies:
            enemy.health -= self._get_damage(damage, radius,
                                             enemy.position.distance_to(explosion_position))
            
    def _get_damage(self, max_damage, radius, distance):
        if distance > radius:
            return 0
        else:
            return int(max_damage * ((radius - distance) / radius))

    def _spawn_airstrike(self, delta_time):
        if self.air_strike is None and \
           (not random.randint(0, int(AIR_STRIKE_FREQUENCY / delta_time))):
            self.air_strike = AirStrike(self.tank.position)

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

        self.enemies = [e for e in self.enemies if abs(e.position - self.tank.position) < ENEMY_DESPAWN_RADIUS]


    def _remove_dead_enemies(self):
        temp_enemies = []
        dead_enemies = 0
        for e in self.enemies:
            if (e.is_dead()):
                dead_enemies+=1
            else:
                temp_enemies.append(e)
        self.enemies = temp_enemies
        self._increment_score(dead_enemies)

        #self.enemies = [e for e in self.enemies if not e.is_dead()]

    def _increment_score(self, dead_enemies):
        self.score += 1 * dead_enemies

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
                self._spawn_an_enemy()

    def _spawn_an_enemy(self):
        angle = (random.randint(0, 1000) / 1000) * math.pi * 2
        self.enemies.append(Enemy(self.tank.position + vec2_from_direction(angle, 300)))



