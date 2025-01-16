import pygame
from utils import scale_image

# pygame 초기화
if not pygame.get_init():
    pygame.init()
if not pygame.font.get_init():
    pygame.font.init()

# 화면 크기 및 프레임 속도
WIDTH, HEIGHT = 800, 600
FPS = 60

# 이미지 로드
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
FINISH = pygame.transform.rotate(pygame.image.load("imgs/finish.png"), 90)

RED_CAR_IMG = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
BLUE_CAR_IMG = scale_image(pygame.image.load("imgs/blue-car.png"), 0.55)

TRAP = pygame.transform.scale(pygame.image.load("imgs/trap.png"), (25, 15))
BOOST = pygame.transform.scale(pygame.image.load("imgs/boost.png"), (25, 15))

# 마스크 생성
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH_MASK = pygame.mask.from_surface(FINISH)

# 위치
FINISH_POSITION = (445, 3)
MAIN_FONT = pygame.font.SysFont("comicsans", 35)
