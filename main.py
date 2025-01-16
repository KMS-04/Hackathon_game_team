import pygame
import time
from constants import WIN, FPS, MAIN_FONT, GRASS, TRACK, FINISH, FINISH_POSITION, TRACK_BORDER, TRAP, BOOST
from game_info import GameInfo
from items import generate_random_positions, TRAP_WIDTH, TRAP_HEIGHT, BOOST_WIDTH, BOOST_HEIGHT
from collision import handle_collision
from car import PlayerCar, AICar
from utils import blit_text_center

pygame.init()
pygame.font.init()

# Draw Function
def draw(win, images, player_car, ai_car, game_info, traps, boosts):
    for img, pos in images:
        win.blit(img, pos)

    for trap in traps:
        win.blit(TRAP, trap)

    for boost in boosts:
        win.blit(BOOST, boost)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    WIN.blit(level_text, (WIN.get_width() - level_text.get_width() - 10, 10))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    WIN.blit(time_text, (WIN.get_width() - time_text.get_width() - 10, 50))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    WIN.blit(vel_text, (WIN.get_width() - vel_text.get_width() - 10, 90))

    player_car.draw(win)
    ai_car.draw(win)
    pygame.display.update()

# Move Player
def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

# Main Functionality
def main():
    run = True
    clock = pygame.time.Clock()
    images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

    player_car = PlayerCar(max_vel=4, rotation_vel=6)
    ai_car = AICar(max_vel=4, rotation_vel=6, path=[(200, 200), (300, 300), (400, 200), (300, 100)])
    game_info = GameInfo()

    traps = generate_random_positions(5, TRAP_WIDTH, TRAP_HEIGHT)
    boosts = generate_random_positions(5, BOOST_WIDTH, BOOST_HEIGHT)

    while run:
        clock.tick(FPS)

        if not game_info.started:
            blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        draw(WIN, images, player_car, ai_car, game_info, traps, boosts)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        move_player(player_car)
        ai_car.move()

        # Check for trap collision
        for trap in traps:
            if player_car.collide(pygame.mask.from_surface(TRAP), *trap):
                traps.remove(trap)
                traps.append(generate_random_positions(1, TRAP_WIDTH, TRAP_HEIGHT)[0])
                player_car.apply_effect("trap")
                break

        # Check for boost collision
        for boost in boosts:
            if player_car.collide(pygame.mask.from_surface(BOOST), *boost):
                boosts.remove(boost)
                boosts.append(generate_random_positions(1, BOOST_WIDTH, BOOST_HEIGHT)[0])
                player_car.apply_effect("boost")
                break

        handle_collision(player_car, game_info, ai_car)
        handle_collision(ai_car, game_info, player_car)

        if game_info.game_finished():
            blit_text_center(WIN, MAIN_FONT, "You won the game!")
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()
            ai_car.reset()

    pygame.quit()

if __name__ == "__main__":
    main()
