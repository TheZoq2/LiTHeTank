import sdl2.ext

RESOURCES = sdl2.ext.Resources(__file__, "resources")
FONTMANAGER = sdl2.ext.FontManager(RESOURCES.get_path("pixeled.ttf"), size=5)

def render_sprites(sprites, renderer):
    rect = sdl2.rect.SDL_Rect(0, 0, 0, 0)

    for sprite in sprites:
        rect.x = sprite.x
        rect.y = sprite.y
        rect.w, rect.h = sprite.size

        scale_x, scale_y = sprite.scale
        rect.w = int(scale_x * rect.w)
        rect.h = int(scale_y * rect.h)

        if sprite.center:
            rect.x -= rect.w // 2
            rect.y -= rect.h // 2

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
    sprite.center = True
    return sprite

def create_rect(color, size, factory):
    sprite = factory.from_color(color, size=size)
    sprite.angle = 0
    sprite.scale = (1, 1)
    sprite.center = True
    return sprite

def render_text(text, factory):
    surface = FONTMANAGER.render(text)
    sprite = factory.from_surface(surface)
    sprite.angle = 0
    sprite.scale = (1, 1)
    sprite.center = True
    return sprite
