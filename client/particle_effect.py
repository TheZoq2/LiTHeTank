import vec
import render_util as ru


def load_smoke_particles(factory):
    return [
        ru.load_sprite("smoke1.png", factory),
        ru.load_sprite("smoke2.png", factory),
        ru.load_sprite("smoke3.png", factory),
        ru.load_sprite("smoke4.png", factory),
        ru.load_sprite("smoke5.png", factory),
        ru.load_sprite("smoke6.png", factory),
        ru.load_sprite("smoke7.png", factory)
    ]

def load_explosion_particles(factory):
    return [
        ru.load_sprite("explosion1.png", factory),
        ru.load_sprite("explosion2.png", factory),
        ru.load_sprite("explosion3.png", factory),
        ru.load_sprite("explosion4.png", factory),
        ru.load_sprite("explosion5.png", factory),
        ru.load_sprite("explosion6.png", factory)
    ]

def create_smoke_particle(pos, sprite_list):
    return Particle(pos, vec.Vec2(0,10), 1.3, sprite_list)

def create_explosion_particle(pos, vel, sprite_list):
    return Particle(pos, vel, 0.1, sprite_list)


class Particle:
    def __init__(self, pos, vel, sprite_time, sprite_list):
        self.pos = pos
        self.vel = vel
        self.sprite_list = sprite_list
        self.sprite_time = sprite_time
        self.current_index = 0
        self.this_index_time = 0
        self.is_alive = True

    def update(self, delta_t):
        self.pos += self.vel * delta_t
        self.this_index_time += delta_t

        if self.this_index_time > self.sprite_time:
            self.current_index += 1
            self.this_index_time = 0

            print(self.current_index)
            if self.current_index >= len(self.sprite_list):
                self.is_alive = False

    def render(self, renderer):
        if self.is_alive:
            sprite = self.sprite_list[self.current_index]
            sprite.x = round(self.pos.x)
            sprite.y = round(self.pos.y)
            ru.render_sprites([sprite], renderer)
