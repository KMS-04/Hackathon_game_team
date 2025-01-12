import pygame
import random
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN, K_LEFT, K_RIGHT

class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.movement = {"up": False, "down": False, "left": False, "right": False}
        self.stopped = False
        self.stop_timer = 0

    def move(self):
        if self.stopped:
            if pygame.time.get_ticks() - self.stop_timer >= 2000:
                self.stopped = False
            return

        if self.movement["up"]:
            self.rect.y -= self.speed
        if self.movement["down"]:
            self.rect.y += self.speed
        if self.movement["left"]:
            self.rect.x -= self.speed
        if self.movement["right"]:
            self.rect.x += self.speed

        # 화면 경계 제한
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x > 1200 - self.rect.width:
            self.rect.x = 1200 - self.rect.width
        if self.rect.y > 900 - self.rect.height:
            self.rect.y = 900 - self.rect.height


class Banana(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/banana.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class gamespace():
    def main(self):
        pygame.init()
        self.size = self.width, self.height = 1200, 900
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Mario Kart")

        self.background = pygame.image.load("assets/mario-kart-circuit.png")

        # 출발선 앞에 플레이어 배치
        self.start_line_x, self.start_line_y = 100, 420
        self.mario = Player("assets/mario.png", self.start_line_x, self.start_line_y)
        self.yoshi = Player("assets/yoshi.png", self.start_line_x, self.start_line_y + 60)

        # 바나나 배치
        self.bananas = pygame.sprite.Group()
        for _ in range(5):
            x = random.randint(200, 1000)
            y = random.randint(200, 700)
            banana = Banana(x, y)
            self.bananas.add(banana)

        self.clock = pygame.time.Clock()
        self.running = True
        self.winner = None

        while self.running:
            self.clock.tick(60)
            self.handle_events()

            if not self.winner:
                self.update_game()
            self.render()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    self.mario.movement["up"] = True
                elif event.key == K_DOWN:
                    self.mario.movement["down"] = True
                elif event.key == K_LEFT:
                    self.mario.movement["left"] = True
                elif event.key == K_RIGHT:
                    self.mario.movement["right"] = True
            elif event.type == KEYUP:
                if event.key == K_UP:
                    self.mario.movement["up"] = False
                elif event.key == K_DOWN:
                    self.mario.movement["down"] = False
                elif event.key == K_LEFT:
                    self.mario.movement["left"] = False
                elif event.key == K_RIGHT:
                    self.mario.movement["right"] = False

    def update_game(self):
        self.mario.move()
        self.update_yoshi()

        if pygame.sprite.spritecollideany(self.mario, self.bananas):
            self.mario.stopped = True
            self.mario.stop_timer = pygame.time.get_ticks()
        if pygame.sprite.spritecollideany(self.yoshi, self.bananas):
            self.yoshi.stopped = True
            self.yoshi.stop_timer = pygame.time.get_ticks()

        if not self.is_on_track(self.mario):
            self.reset_player(self.mario)
        if not self.is_on_track(self.yoshi):
            self.reset_player(self.yoshi)

        if self.mario.rect.x > 1100:
            self.winner = "mario"
        if self.yoshi.rect.x > 1100:
            self.winner = "yoshi"

    def update_yoshi(self):
        directions = ["up", "down", "left", "right"]
        if random.randint(0, 20) == 0:
            self.yoshi.movement = {d: False for d in directions}
            direction = random.choice(directions)
            self.yoshi.movement[direction] = True
        self.yoshi.move()

    def reset_player(self, player):
        player.rect.x = self.start_line_x
        player.rect.y = self.start_line_y

    def is_on_track(self, player):
        color = self.background.get_at((player.rect.centerx, player.rect.centery))
        return color != (0, 255, 0, 255)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        if self.winner == "mario":
            winner_image = pygame.image.load("assets/mario_winner.png")
            self.screen.blit(winner_image, (400, 300))
        elif self.winner == "yoshi":
            winner_image = pygame.image.load("assets/yoshi_winner.png")
            self.screen.blit(winner_image, (400, 300))
        else:
            self.bananas.draw(self.screen)
            self.screen.blit(self.mario.image, self.mario.rect)
            self.screen.blit(self.yoshi.image, self.yoshi.rect)

        pygame.display.flip()


if __name__ == "__main__":
    gs = gamespace()
    gs.main()
