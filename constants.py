# constants.py
import pygame
from utils import scale_image

pygame.init()
pygame.font.init()

# Load images
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
TRACK_MASK = pygame.mask.from_threshold(TRACK, (33, 33, 33), (10, 10, 10))  # 흰색 도로만 추출
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH2 = pygame.image.load("imgs/finish.png")
FINISH = pygame.transform.rotate(FINISH2, 90)  # 90도 회전
FINISH_MASK2 = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (445, 3)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/blue-car.png"), 0.55)
TRAP = pygame.transform.scale(pygame.image.load("imgs/trap.png"), (25, 15))
BOOST = pygame.transform.scale(pygame.image.load("imgs/boost.png"), (25, 15))

FINISH_MASK = pygame.mask.from_surface(pygame.transform.scale(FINISH2, (FINISH.get_width() + 10, FINISH.get_height() + 10)))

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 35)
FPS = 60