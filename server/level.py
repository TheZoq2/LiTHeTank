import sdl2.ext
from vec import Vec2, vec2_from_direction
import random

DEFAULT_ENEMY_SIZE = 5
DEFAULT_BULLET_DAMAGE = 10
DEFAULT_BULLET_SPEED = 2

DEFAULT_ENEMY_HEALTH = 20

# The default probability for the enemies. Higher numbers result in lower frequencies
DEFAULT_FIRING_FREQUENCY = 100

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

    FIRE_LEFT = 0
    FIRE_RIGHT = 1
    
    def __init__(self, tank):
        self.tank = tank
        self.enemies = []
        self.bullets = []

    def update(self):
        if self.tank.firing_left:
            self._fire_tank(FIRE_LEFT)
            self.tank.firing_left = False
        else:
            self._fire_tank(FIRE_RIGHT)
            self.firing_right = False

    def _fire_tank(self, cannon):
        # TODO differentiate between left and right
        self.bullets.append(Bullet(self.tank.position, 
                                  self.tank.gun_angle + self.tank.angle))
    
    def _handle_bullet_collisions(self):
        pass

    def _update_bullet_positions(self):
        for bullet in self.bullets:
            bullet.position += bullet.velocity

    def _update_enemy_positions(self):
        pass
    
    def _remove_dead_enemies(self):
        self.enemies = [e for e in self.enemies if not e.is_dead()]

    def _fire_enemies(self):
        for enemy in self.enemies:
            should_fire = not random.randint(0, enemy.firing_frequency)

            # if the random number was 0, fire
            if should_fire:
                self._enemy_fire(enemy)
                
    def _enemy_fire(self, enemy):
        pass
    
    def _spawn_enemy(self):
        randx = random.randint(0, 1000)
        randy = random.randint(0, 1000)
        self.enemies.append(Enemy(Vec2(randx, randy)))
        

