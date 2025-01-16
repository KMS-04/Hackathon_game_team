import pygame


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width() / 2 - render.get_width() / 2,
                      win.get_height() / 2 - render.get_height() / 2))
    
def create_border_mask(surface):
    """
    차량의 테두리 마스크 생성
    :param surface: 차량 이미지 (pygame.Surface)
    :return: 테두리 마스크 (pygame.Mask)
    """
    original_mask = pygame.mask.from_surface(surface)
    border_mask = pygame.mask.Mask(surface.get_size())

    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            if original_mask.get_at((x, y)) == 1:
                # 테두리의 픽셀만 포함
                if (
                    x == 0 or y == 0 or
                    x == surface.get_width() - 1 or y == surface.get_height() - 1 or
                    original_mask.get_at((x - 1, y)) == 0 or
                    original_mask.get_at((x + 1, y)) == 0 or
                    original_mask.get_at((x, y - 1)) == 0 or
                    original_mask.get_at((x, y + 1)) == 0
                ):
                    border_mask.set_at((x, y), 1)

    return border_mask
