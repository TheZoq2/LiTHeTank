from vec import Vec2, vec2_from_direction
import random

DEFAULT_ENEMY_SIZE = 5
DEFAULT_BULLET_DAMAGE = 10
DEFAULT_BULLET_SPEED = 2

class Enemy():

    def __init__(self, position, size=DEFAULT_ENEMY_SIZE):
        self.position = position
        self.health = 100
        self.size = size

    def is_dead(self):
        return self.health <= 0


class Bullet():

    def __init__(self, position, angle, speed=DEFAULT_BULLET_SPEED, damage=DEFAULT_BULLET_DAMAGE):
        self.position = position
        self.velocity = vec2_from_direction(angle, speed)
        self.damage = damage


class Level():
    
    def __init__(self, tank):
        self.tank = tank
        self.enemies = []
        self.bullets = []

    def update(self):
        if self.tank.firing:
            self._fire_tank
            self.tank.firing = False

    def _fire_tank(self):
        self.bullets.append(Bullet(self.tank.position, 
                                  self.tank.gun_angle + self.tank.angle))

    def _fire_enemies(self):
        pass
    
    def _spawn_enemy(self):
        randx = random.randint(0, 1000)
        randy = random.randint(0, 1000)
        self.enemies.append(Enemy(Vec2(randx, randy)))
        
