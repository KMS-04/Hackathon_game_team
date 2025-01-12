import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load("assets/yoshi.png")  # 요시 이미지
        self.rect = self.image.get_rect()
        self.rect.x = 300  # 초기 x 위치
        self.rect.y = 100  # 초기 y 위치
        self.speed = 2  # AI 이동 속도

    def tick(self):
        # 간단한 랜덤 움직임 로직
        direction = random.choice(['up', 'down', 'left', 'right'])
        if direction == 'up':
            self.rect.y -= self.speed
        elif direction == 'down':
            self.rect.y += self.speed
        elif direction == 'left':
            self.rect.x -= self.speed
        elif direction == 'right':
            self.rect.x += self.speed

        # 화면 경계 내로 제한
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x > 640 - self.rect.width:
            self.rect.x = 640 - self.rect.width
        if self.rect.y > 480 - self.rect.height:
            self.rect.y = 480 - self.rect.height
