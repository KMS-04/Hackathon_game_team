# racing_env.py
import gym
import numpy as np
from gym import spaces
import pygame
import time

from utils import scale_image, blit_text_center
from cars import PlayerCar, AICar
from game_info import GameInfo
import items

class RacingEnv(gym.Env):
    """
    - 사람(플레이어)가 WASD로 'player_car'를 조작
    - 'ai_car'는 DQN(강화학습) 액션으로 움직이는 구조
    """

    def __init__(self, render_mode=False):
        super(RacingEnv, self).__init__()
        pygame.init()
        pygame.font.init()

        self.render_mode = render_mode
        self.FPS = 60
        self.clock = pygame.time.Clock()

        self.MAIN_FONT = pygame.font.SysFont("comicsans", 35)

        # === (1) 이미지/마스크 로드 (main.py 참고) ===
        self._load_images_and_masks()
        PlayerCar.IMG = self.RED_CAR
        AICar.IMG = self.BLUE_CAR


        # === (2) Gym 환경 정의 ===
        # AI 차를 조작할 액션: 4가지 이산 (0=가만히/감속, 1=전진, 2=좌+전진, 3=우+전진)
        self.action_space = spaces.Discrete(4)

        # 관측(Observation): AI 차의 [x, y, vel, angle, total_distance] (예시)
        high = np.array([self.WIDTH, self.HEIGHT,  10,  360,  999999], dtype=np.float32)
        low  = np.array([     0,         0,        0,    0,       0],  dtype=np.float32)
        self.observation_space = spaces.Box(low, high, shape=(5,), dtype=np.float32)

        # 최대 스텝 수(타임아웃)
        self.max_steps = 2000
        self.current_step_count = 0

        # (옵션) Pygame 화면 생성
        self.WIN = None
        if self.render_mode:
            self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Racing Env: Player WASD, AI Car with DQN")

        # 초깃값 설정
        self.reset()

    def reset(self):
        """
        매 에피소드(학습에서 말하는 한 판) 시작 시 게임 전체를 초기화
        """
        self.current_step_count = 0
        self.game_info = GameInfo()
        self.game_info.start_level()  # 대기 없이 시작

        # 차량 설정
        self.player_car = PlayerCar(max_vel=4, rotation_vel=6)
        # AI 차량에 path는 주지 않음 (DQN이 제어할 거므로)
        self.ai_car = AICar(max_vel=4, rotation_vel=6, path=[])  

        # 아이템 재생성
        self.BOOST_WIDTH, self.BOOST_HEIGHT = self.BOOST_IMG.get_width(), self.BOOST_IMG.get_height()
        self.TRAP_WIDTH, self.TRAP_HEIGHT = self.TRAP_IMG.get_width(), self.TRAP_IMG.get_height()
        self.traps = items.generate_random_positions(5, self.TRAP_WIDTH, self.TRAP_HEIGHT)
        self.boosts = items.generate_random_positions(5, self.BOOST_WIDTH, self.BOOST_HEIGHT)

        # 관측 반환
        return self._get_obs()

    def step(self, action):
        """
        한 스텝 (1프레임) 진행:
        1) 플레이어 = WASD 입력 처리 → player_car 이동
        2) AI 차   = DQN action 적용
        3) 충돌/아이템/결승선 체크, 보상 계산
        4) (obs, reward, done, info) 반환
        """
        self.current_step_count += 1

        # ------ (1) 플레이어 WASD 조작 ------
        self._handle_player_input(self.player_car)

        # ------ (2) AI 차량에 RL 액션 적용 ------
        self._apply_action(self.ai_car, action)

        # ------ (3) 나머지 게임 로직(아이템 충돌, finish 체크 등) ------
        # 아이템 효과 해제
        if time.time() >= self.ai_car.effect_end_time:
            self.ai_car.clear_effect()

        # 플레이어 & AI 아이템 충돌 로직 (원한다면 플레이어도 부스트/트랩에 영향)
        self._check_item_collision(self.player_car)
        self._check_item_collision(self.ai_car)

        # 충돌 처리(트랙, 결승선, 차량 간)
        self._handle_collision(self.player_car, self.game_info, opponent_car=self.ai_car)
        self._handle_collision(self.ai_car, self.game_info, opponent_car=self.player_car)

        # ------ (4) 보상 계산 & done 판단 ------
        reward = self._calculate_reward()
        done = self.game_info.game_finished() or (self.current_step_count >= self.max_steps)

        # 관측
        obs = self._get_obs()
        info = {}

        # 렌더링
        if self.render_mode:
            self.render()

        return obs, reward, done, info

    def render(self, mode='human'):
        """pygame 창에 그리는 함수 (학습 중에는 보통 끔)"""
        if not self.WIN:
            return
        self._draw()
        pygame.display.update()
        self.clock.tick(self.FPS)

    def _draw(self):
        """기존 main.py의 draw() 기반으로 구현 (배경, 아이템, 텍스트, 차량 그림)"""
        for img, pos in self.images:
            self.WIN.blit(img, pos)

        for trap_pos in self.traps:
            self.WIN.blit(self.TRAP_IMG, trap_pos)
        for boost_pos in self.boosts:
            self.WIN.blit(self.BOOST_IMG, boost_pos)

        level_text = self.MAIN_FONT.render(f"Level {self.game_info.level}", True, (255,255,255))
        self.WIN.blit(level_text, (self.WIDTH - level_text.get_width() - 10, 10))

        time_text = self.MAIN_FONT.render(f"Time: {self.game_info.get_level_time()}s", True, (255,255,255))
        self.WIN.blit(time_text, (self.WIDTH - time_text.get_width() - 10, 50))

        vel_text = self.MAIN_FONT.render(f"AI Vel: {round(self.ai_car.vel,1)}px/s", True, (255,255,255))
        self.WIN.blit(vel_text, (self.WIDTH - vel_text.get_width() - 10, 90))

        self.player_car.draw(self.WIN)
        self.ai_car.draw(self.WIN)

        # (선택) pygame event 처리 (창 닫기 등)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit("User closed the window")

    # --------------------------------------------------
    # 내부 보조 함수들
    # --------------------------------------------------

    def _handle_player_input(self, car):
        """
        기존 main.py의 move_player() 함수를 여기로 옮겨옴.
        플레이어가 WASD 누르면 그에 맞춰 car 조작
        """
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_a]:
            car.rotate(left=True)
        if keys[pygame.K_d]:
            car.rotate(right=True)
        if keys[pygame.K_w]:
            moved = True
            car.move_forward()
        if keys[pygame.K_s]:
            moved = True
            car.move_backward()

        if not moved:
            car.reduce_speed()

    def _apply_action(self, ai_car, action):
        """
        DQN 액션을 AI차량에 적용
        0: 가만히(감속), 1: 전진, 2: 좌회전+전진, 3: 우회전+전진
        """
        if action == 0:
            ai_car.reduce_speed()
        elif action == 1:
            ai_car.move_forward()
        elif action == 2:
            ai_car.rotate(left=True)
            ai_car.move_forward()
        elif action == 3:
            ai_car.rotate(right=True)
            ai_car.move_forward()

    def _check_item_collision(self, car):
        """
        car가 트랩/부스트 아이템과 충돌하면 효과 부여
        (원한다면 player_car도 아이템 먹게 할 수 있음)
        """
        # 트랩 충돌
        for trap_pos in self.traps:
            if car.collide(self.TRAP_MASK, *trap_pos):
                self.traps.remove(trap_pos)
                new_trap = items.generate_random_positions(1, self.TRAP_WIDTH, self.TRAP_HEIGHT)
                if new_trap:
                    self.traps.append(new_trap[0])
                car.apply_effect("trap")
                break

        # 부스트 충돌
        for boost_pos in self.boosts:
            if car.collide(self.BOOST_MASK, *boost_pos):
                self.boosts.remove(boost_pos)
                new_boost = items.generate_random_positions(1, self.BOOST_WIDTH, self.BOOST_HEIGHT)
                if new_boost:
                    self.boosts.append(new_boost[0])
                car.apply_effect("boost")
                break

    def _handle_collision(self, car, game_info, opponent_car=None):
        """기존 handle_collision() 로직(트랙 경계, 결승선, 차량 간 충돌 등)"""
        if car.collide(self.TRACK_BORDER_MASK):
            car.bounce()
        else:
            finish_poi = car.collide(self.FINISH_MASK, *self.FINISH_POSITION)
            if finish_poi:
                if not game_info.is_ready_for_finish(car):
                    car.bounce()
                    return
                # 플레이어가 결승선 통과
                if car is self.player_car:
                    if game_info.level < game_info.LEVELS:
                        game_info.next_level()
                        car.reset()
                        if opponent_car: opponent_car.reset()
                    else:
                        blit_text_center(self.WIN, self.MAIN_FONT, "You (Human) won!!")
                        pygame.display.update()
                        pygame.time.wait(2000)
                        game_info.reset()
                        car.reset()
                        if opponent_car: opponent_car.reset()

                else:
                    # AI 차가 결승선 통과
                    blit_text_center(self.WIN, self.MAIN_FONT, "AI Wins!")
                    pygame.display.update()
                    pygame.time.wait(2000)
                    game_info.reset()
                    car.reset()
                    if opponent_car: opponent_car.reset()

        # 차량 간 충돌
        if opponent_car:
            if car.collide(opponent_car.border_mask, opponent_car.x, opponent_car.y):
                car.bounce()
                opponent_car.bounce()

        # 마지막 위치 업데이트
        car.last_position = (car.x, car.y)

    def _calculate_reward(self):
        """
        AI 차량(ai_car)에 대한 보상 설계 (예시)
        - 속도 * 0.1
        - 벽 충돌 시 벌점
        - 결승선 통과 시 큰 보상? (위 handle_collision에서 처리하거나, 여기서 해도 됨)
        """
        reward = 0.0

        # 속도가 높으면 약간의 보상
        reward += 0.1 * self.ai_car.vel

        # (옵션) 만약 bounce가 발생했다면 -1 (별도 변수로 기록해야 정확히 체크 가능)
        # 예: self.ai_car.bounced = True 식으로 표시 → reward -= 1

        return reward

    def _get_obs(self):
        """
        관측: AI 차량 정보
        [ai_car.x, ai_car.y, ai_car.vel, ai_car.angle, ai_car.total_distance]
        """
        return np.array([
            self.ai_car.x,
            self.ai_car.y,
            self.ai_car.vel,
            self.ai_car.angle,
            self.ai_car.total_distance
        ], dtype=np.float32)

    def _load_images_and_masks(self):
        """main.py에서 이미지/마스크 로드 부분을 옮겨온 함수"""
        from utils import scale_image
        import pygame

        # trap, boost 이미지 로드
        self.TRAP_IMG = pygame.transform.scale(
            pygame.image.load("imgs/trap.png"), (25, 15)
        )
        self.BOOST_IMG = pygame.transform.scale(
            pygame.image.load("imgs/boost.png"), (25, 15)
        )

        # 여기서 꼭 마스크도 생성:
        self.TRAP_MASK = pygame.mask.from_surface(self.TRAP_IMG)
        self.BOOST_MASK = pygame.mask.from_surface(self.BOOST_IMG)


        self.GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
        self.TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
        self.TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)

        self.FINISH = pygame.image.load("imgs/finish.png")
        self.FINISH = pygame.transform.rotate(self.FINISH, 90)
        self.FINISH_POSITION = (445, 3)

        self.RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
        self.BLUE_CAR = scale_image(pygame.image.load("imgs/blue-car.png"), 0.55)
        self.TRAP_IMG = pygame.transform.scale(pygame.image.load("imgs/trap.png"), (25, 15))
        self.BOOST_IMG = pygame.transform.scale(pygame.image.load("imgs/boost.png"), (25, 15))

        self.TRACK_BORDER_MASK = pygame.mask.from_surface(self.TRACK_BORDER)
        self.FINISH_MASK = pygame.mask.from_surface(
            pygame.transform.scale(self.FINISH, (self.FINISH.get_width()+10, self.FINISH.get_height()+10))
        )
        track_mask = pygame.mask.from_threshold(self.TRACK, (33,33,33), (10,10,10))

        self.WIDTH, self.HEIGHT = self.TRACK.get_width(), self.TRACK.get_height()
        items.TRACK_MASK = track_mask
        items.WIDTH, items.HEIGHT = self.WIDTH, self.HEIGHT

        self.images = [
            (self.GRASS, (0, 0)),
            (self.TRACK, (0, 0)),
            (self.FINISH, self.FINISH_POSITION),
            (self.TRACK_BORDER, (0, 0))
        ]