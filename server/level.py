from vec import Vec2, vec2_from_direction

DEFAULT_ENEMY_SIZE = 5
DEFAULT_BULLET_DAMAGE = 10

class Enemy():

    def __init__(self, size=DEFAULT_ENEMY_SIZE):
        self.position = Vec2(0, 0)
        self.health = 100
        self.size = size


class Bullet():

    def __init__(self, angle, speed, damage=DEFAULT_BULLET_DAMAGE):
        self.position = Vec2(0, 0)
        self.velocity = vec2_from_direction(angle, speed)


class Level():
    
    def __init__(self, tank):
        self.tank = tank
        self.enemies = []
        self.bullets = []

    def step(self):
        pass


