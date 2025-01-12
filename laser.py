import pygame
import math

class Laser(pygame.sprite.Sprite):
    def __init__(self, angle, position, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load("laser.png")  # Ensure this image exists
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.angle = angle
        self.speed = 10  # 레이저 이동 속도

    def tick(self):
        # 레이저의 각도에 따라 위치 업데이트
        rad_angle = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(rad_angle)
        self.rect.y -= self.speed * math.sin(rad_angle)

        # 레이저가 화면 밖으로 나가면 제거
        if (self.rect.x < 0 or self.rect.x > 640 or 
            self.rect.y < 0 or self.rect.y > 480):
            if self in self.gs.laser_list:  # 레이저 리스트에서 제거
                self.gs.laser_list.remove(self)
