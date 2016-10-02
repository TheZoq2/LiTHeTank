import sdl2.ext
from vec import Vec2

RESOURCES = sdl2.ext.Resources(__file__, "resources")

def render_sprites(sprites, renderer, cam_pos = Vec2(0, 0)):
    rect = sdl2.rect.SDL_Rect(0, 0, 0, 0)

    for sprite in sprites:
        rect.x = sprite.x - cam_pos.x
        rect.y = sprite.y - cam_pos.y
        rect.w, rect.h = sprite.size

        scale_x, scale_y = sprite.scale
        rect.w = int(scale_x * rect.w)
        rect.h = int(scale_y * rect.h)

        if sdl2.render.SDL_RenderCopyEx(renderer.sdlrenderer,
                                        sprite.texture,
                                        None,
                                        rect,
                                        sprite.angle,
                                        None,
                                        sdl2.render.SDL_FLIP_NONE) == -1:
            return False

def load_sprite(path, factory):
    sprite = factory.from_image(RESOURCES.get_path(path))
    sprite.angle = 0
    sprite.scale = (1, 1)
    return sprite

def create_rect(color, size, factory):
    sprite = factory.from_color(color, size=size)
    sprite.angle = 0
    sprite.scale = (1, 1)
    return sprite
