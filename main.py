import pygame
import random
import time
import math

import torch
import numpy as np
from dqn_agent import DQNAgent  # ← 본인의 DQN 에이전트 파일 경로

from utils import scale_image, blit_text_center
from cars import PlayerCar, AICar
from cars import create_border_mask
from game_info import GameInfo
import items

pygame.init()
pygame.font.init()

# 기본 설정
FPS = 60
MAIN_FONT = pygame.font.SysFont("comicsans", 35)

# 이미지 로드 및 변환
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)

FINISH = pygame.image.load("imgs/finish.png")
FINISH = pygame.transform.rotate(FINISH, 90)  # 90도 회전
FINISH_POSITION = (445, 3)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
BLUE_CAR = scale_image(pygame.image.load("imgs/blue-car.png"), 0.55)
TRAP = pygame.transform.scale(pygame.image.load("imgs/trap.png"), (25, 15))
BOOST = pygame.transform.scale(pygame.image.load("imgs/boost.png"), (25, 15))

# 마스크 생성
TRACK_MASK = pygame.mask.from_threshold(TRACK, (33, 33, 33), (10, 10, 10))
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH_MASK = pygame.mask.from_surface(
    pygame.transform.scale(FINISH, (FINISH.get_width() + 10, FINISH.get_height() + 10))
)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

# cars.py에서 가져온 클래스들에 이미지 할당
PlayerCar.IMG = RED_CAR
AICar.IMG = BLUE_CAR

# items.py 전역변수 설정
items.TRACK_MASK = TRACK_MASK
items.WIDTH, items.HEIGHT = WIDTH, HEIGHT

# 아이템(트랩, 부스트) 마스크
TRAP_MASK = pygame.mask.from_surface(TRAP)
BOOST_MASK = pygame.mask.from_surface(BOOST)

# 이미지 목록
images = [
    (GRASS, (0, 0)),
    (TRACK, (0, 0)),
    (FINISH, FINISH_POSITION),
    (TRACK_BORDER, (0, 0)),
]

# 게임 정보, 플레이어/AI 차량 생성
game_info = GameInfo()
player_car = PlayerCar(max_vel=4, rotation_vel=6)
ai_car = AICar(max_vel=4, rotation_vel=6, path=[])

# 아이템(트랩, 부스트) 위치 생성
BOOST_WIDTH, BOOST_HEIGHT = BOOST.get_width(), BOOST.get_height()
TRAP_WIDTH, TRAP_HEIGHT = TRAP.get_width(), TRAP.get_height()

traps = items.generate_random_positions(5, TRAP_WIDTH, TRAP_HEIGHT)
boosts = items.generate_random_positions(5, BOOST_WIDTH, BOOST_HEIGHT)

# main.py (일부)
agent = DQNAgent(state_dim=5, action_dim=4)  # state_dim=5, action_dim=4 가정
agent.q_network.load_state_dict(torch.load("racing_dqn.pth"))
agent.q_network.eval()
agent.eps = 0.0  # 탐색 종료 (학습된 정책만 사용)


def draw(win, images, player_car, ai_car, game_info, traps, boosts):
    for img, pos in images:
        win.blit(img, pos)

    for trap_pos in traps:
        win.blit(TRAP, trap_pos)

    for boost_pos in boosts:
        win.blit(BOOST, boost_pos)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (WIDTH - time_text.get_width() - 10, 50))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (WIDTH - vel_text.get_width() - 10, 90))

    player_car.draw(win)
    ai_car.draw(win)
    pygame.display.update()


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


def handle_collision(car, game_info, opponent_car=None):
    # 트랙 경계 충돌 처리
    if car.collide(TRACK_BORDER_MASK):
        car.bounce()
    else:
        # 결승선 충돌 확인
        finish_poi = car.collide(FINISH_MASK, *FINISH_POSITION)
        if finish_poi:
            if not game_info.is_ready_for_finish(car):
                car.bounce()
                return

            # 플레이어 차일 경우
            if car is player_car:
                if game_info.level < game_info.LEVELS:
                    game_info.next_level()
                    car.reset()
                    if opponent_car:
                        opponent_car.reset()
                else:
                    blit_text_center(WIN, MAIN_FONT, "You won against AI!!")
                    pygame.display.update()
                    pygame.time.wait(5000)
                    game_info.reset()
                    car.reset()
                    if opponent_car:
                        opponent_car.reset()
            else:
                # AI 차량이 결승선 통과 시
                blit_text_center(WIN, MAIN_FONT, "AI Wins!")
                pygame.display.update()
                pygame.time.wait(5000)
                game_info.reset()
                car.reset()
                if opponent_car:
                    opponent_car.reset()

    # 플레이어와 AI 간 충돌
    if opponent_car:
        if car.collide(opponent_car.border_mask, opponent_car.x, opponent_car.y):
            car.bounce()
            opponent_car.bounce()

    # 마지막 위치 업데이트
    car.last_position = (car.x, car.y)

def apply_dqn_action(car, action):
    # 0: 감속/가만히, 1: 전진, 2: 좌회전+전진, 3: 우회전+전진
    if action == 0:
        car.reduce_speed()
    elif action == 1:
        car.move_forward()
    elif action == 2:
        car.rotate(left=True)
        car.move_forward()
    elif action == 3:
        car.rotate(right=True)
        car.move_forward()


def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)

        # 레벨 시작 전 대기
        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        # 아이템 효과 해제 체크
        if time.time() >= player_car.effect_end_time:
            player_car.clear_effect()

        # 화면 그리기
        draw(WIN, images, player_car, ai_car, game_info, traps, boosts)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # 플레이어 이동 
        move_player(player_car)

        # AI 이동
        #  1) 상태 관측
        state = np.array([ai_car.x, ai_car.y, ai_car.vel, ai_car.angle, ai_car.total_distance], dtype=np.float32)
        #  2) 액션 받기
        action = agent.select_action(state)
        #  3) 액션 적용
        apply_dqn_action(ai_car, action)



        # 트랩 충돌
        for trap_pos in traps:
            if player_car.collide(pygame.mask.from_surface(TRAP), *trap_pos):
                traps.remove(trap_pos)
                new_trap = items.generate_random_positions(1, TRAP_WIDTH, TRAP_HEIGHT)
                if new_trap:
                    traps.append(new_trap[0])
                player_car.apply_effect("trap")
                break

        # 부스트 충돌
        for boost_pos in boosts:
            if player_car.collide(pygame.mask.from_surface(BOOST), *boost_pos):
                boosts.remove(boost_pos)
                new_boost = items.generate_random_positions(1, BOOST_WIDTH, BOOST_HEIGHT)
                if new_boost:
                    boosts.append(new_boost[0])
                player_car.apply_effect("boost")
                break

        # 충돌 처리
        handle_collision(player_car, game_info, opponent_car=ai_car)
        handle_collision(ai_car, game_info, opponent_car=player_car)

        # 레벨/게임 종료 체크
        if game_info.game_finished():
            blit_text_center(WIN, MAIN_FONT, "You won the game!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()
            ai_car.reset()

    pygame.quit()

if __name__ == "__main__":
    main()
