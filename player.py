import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load("assets/mario.png")  # 마리오 이미지
        self.rect = self.image.get_rect()
        self.rect.x = 100  # 초기 x 위치
        self.rect.y = 100  # 초기 y 위치

    def move(self, key_num):
        # 방향키에 따라 플레이어 이동
        if key_num == pygame.K_LEFT:
            self.rect = self.rect.move(-5, 0)
        if key_num == pygame.K_RIGHT:
            self.rect = self.rect.move(5, 0)
        if key_num == pygame.K_UP:
            self.rect = self.rect.move(0, -5)
        if key_num == pygame.K_DOWN:
            self.rect = self.rect.move(0, 5)
