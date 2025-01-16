# collision.py
import pygame
from utils import blit_text_center
from constants import WIN, MAIN_FONT, TRACK_BORDER_MASK, FINISH_MASK, FINISH_POSITION

def handle_collision(car, game_info, opponent_car=None):
    # 트랙 경계 충돌 처리
    if car.collide(TRACK_BORDER_MASK):
        car.bounce()
    else:
        # 결승선 충돌 확인
        finish_poi = car.collide(FINISH_MASK, *FINISH_POSITION)
        if finish_poi:
            if not game_info.is_ready_for_finish(car):
                car.bounce()  # 조건 충족 안 될 경우 반사 처리
                return
            if isinstance(car, car.__class__):
                if game_info.level < game_info.LEVELS:  # 마지막 단계가 아닌 경우
                    game_info.next_level()
                    car.reset()
                    if opponent_car:
                        opponent_car.reset()
                else:  # 최종 단계 완료
                    blit_text_center(WIN, MAIN_FONT, "You won against AI!!")
                    pygame.display.update()
                    pygame.time.wait(5000)
                    game_info.reset()
                    car.reset()
                    if opponent_car:
                        opponent_car.reset()
            else:
                blit_text_center(WIN, MAIN_FONT, "AI Wins!")
                pygame.display.update()
                pygame.time.wait(5000)
                game_info.reset()
                car.reset()
                if opponent_car:
                    opponent_car.reset()

    # AI와 플레이어 차량 간 충돌 처리
    if opponent_car:
        if car.collide(opponent_car.border_mask, opponent_car.x, opponent_car.y):
            car.bounce()
            opponent_car.bounce()

    # 현재 위치를 마지막 위치로 저장
    car.last_position = (car.x, car.y)