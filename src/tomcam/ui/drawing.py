import sdl2


def rounded_rect(renderer, x, y, width, height, radius, color):
    """Filled rounded rectangle drawn with SDL renderer primitives."""
    sdl2.SDL_SetRenderDrawColor(renderer, *color)
    radius = max(0, min(radius, width // 2, height // 2))
    if radius == 0:
        sdl2.SDL_RenderFillRect(renderer, sdl2.SDL_Rect(x, y, width, height))
        return

    sdl2.SDL_RenderFillRect(
        renderer, sdl2.SDL_Rect(x + radius, y, width - 2 * radius, height)
    )
    sdl2.SDL_RenderFillRect(
        renderer, sdl2.SDL_Rect(x, y + radius, width, height - 2 * radius)
    )

    for cy in (y + radius, y + height - radius - 1):
        for cx in (x + radius, x + width - radius - 1):
            for dy in range(-radius, radius + 1):
                dx = int((radius * radius - dy * dy) ** 0.5)
                sdl2.SDL_RenderFillRect(
                    renderer, sdl2.SDL_Rect(cx - dx, cy + dy, 2 * dx + 1, 1)
                )


def outline_rounded_rect(renderer, x, y, width, height, radius, color, thickness=2):
    for inset in range(thickness):
        rounded_rect(renderer, x + inset, y + inset, width - 2 * inset,
                     height - 2 * inset, max(0, radius - inset), color)


