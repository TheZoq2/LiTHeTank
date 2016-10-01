import sdl2.ext

RESOURCES = sdl2.ext.Resources(__file__, "resources")

def render_sprites(sprites, renderer):
    rect = sdl2.rect.SDL_Rect(0, 0, 0, 0)

    for sprite in sprites:
        rect.x = sprite.x
        rect.y = sprite.y
        rect.w, rect.h = sprite.size
        if sdl2.render.SDL_RenderCopyEx(renderer.sdlrenderer,
                                        sprite.texture,
                                        None,
                                        rect,
                                        sprite.angle,
                                        None,
                                        sdl2.render.SDL_FLIP_NONE) == -1:
            return False
    sdl2.render.SDL_RenderPresent(renderer.sdlrenderer)

def load_sprite(path, factory):
    sprite = factory.from_image(RESOURCES.get_path(path))
    sprite.angle = 0
    return sprite
