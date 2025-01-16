import pygame
import time
import math
import random
from utils import scale_image, blit_rotate_center, blit_text_center

pygame.init()
pygame.font.init()

# Load images
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
TRACK_MASK = pygame.mask.from_threshold(TRACK, (33, 33, 33), (10, 10, 10))  # 흰색 도로만 추출
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH = pygame.transform.rotate(FINISH, 90)  # 90도 회전
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (445, 3)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/blue-car.png"), 0.55)
TRAP = pygame.transform.scale(pygame.image.load("imgs/trap.png"), (25, 15))
BOOST = pygame.transform.scale(pygame.image.load("imgs/boost.png"), (25, 15))

FINISH_MASK = pygame.mask.from_surface(pygame.transform.scale(FINISH, (FINISH.get_width() + 10, FINISH.get_height() + 10)))

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 35)
FPS = 60

# Game Info Class
class GameInfo:
    LEVELS = 3
    MIN_DISTANCE = 5000  # 최소 이동 거리 (픽셀)
    MIN_TIME = 20  # 최소 경과 시간 (초)

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)
    
    def is_ready_for_finish(self, car):
        """
        결승선 통과 조건을 충족했는지 확인
        :param car: AbstractCar 객체
        :return: 조건 충족 여부
        """
        if not self.started:
            return False

        # 경과 시간 확인
        elapsed_time = time.time() - self.level_start_time
        if elapsed_time < self.MIN_TIME:
            return False

        # 최소 이동 거리 확인
        if car.total_distance < self.MIN_DISTANCE:
            return False
        
        # 차량 속도와 방향 확인
        if car.vel <= 0:  # 전진 중이 아닐 경우
            return False

        return True
    
def create_border_mask(surface):
    """
    차량의 테두리 마스크 생성
    :param surface: 차량 이미지 (pygame.Surface)
    :return: 테두리 마스크 (pygame.Mask)
    """
    original_mask = pygame.mask.from_surface(surface)
    border_mask = pygame.mask.Mask(surface.get_size())

    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            if original_mask.get_at((x, y)) == 1:
                # 테두리의 픽셀만 포함
                if (
                    x == 0 or y == 0 or
                    x == surface.get_width() - 1 or y == surface.get_height() - 1 or
                    original_mask.get_at((x - 1, y)) == 0 or
                    original_mask.get_at((x + 1, y)) == 0 or
                    original_mask.get_at((x, y - 1)) == 0 or
                    original_mask.get_at((x, y + 1)) == 0
                ):
                    border_mask.set_at((x, y), 1)

    return border_mask

# Abstract Car Class
class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.original_max_vel = max_vel  # 원래 속도 저장
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 270  # 초기 방향
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

        self.boost_stack = 0  # 가속 효과 누적 횟수
        self.slow_stack = 0  # 감속 효과 누적 횟수
        self.effect_end_times = []  # 효과 종료 시간 저장

        self.boosted = False
        self.slowed = False
        self.effect_end_time = 0
        self.last_position = (self.x, self.y)  # 이전 위치
        self.total_distance = 0  # 누적 이동 거리
        self.border_mask = create_border_mask(self.img)  # 테두리 마스크 생성

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()


    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        # 이동 처리
        if abs(self.vel) < 0.01:  # 너무 느리면 멈춤
            self.vel = 0
            return

        # 현재 위치를 이전 위치로 저장
        self.last_position = (self.x, self.y)

        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        # 현재 위치 갱신
        self.y -= vertical
        self.x -= horizontal

        # 누적 이동 거리 계산
        self.total_distance += math.sqrt(vertical**2 + horizontal**2)

    def collide(self, mask, x=0, y=0):
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(self.border_mask, offset)  # 테두리 마스크 사용
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.boosted = False
        self.slowed = False

    def apply_effect(self, effect_type):
        if effect_type == "boost":
            self.boost_stack += 1  # 가속 효과 누적
            self.max_vel = self.original_max_vel * (1.3 ** self.boost_stack)
        elif effect_type == "trap":
            self.slow_stack += 1  # 감속 효과 누적
            self.max_vel = self.original_max_vel * (0.7 ** self.slow_stack)
        
        # 각 효과의 종료 시간을 개별적으로 관리
        self.effect_end_times.append((time.time() + 3, effect_type))  # 효과 타입과 종료 시간 저장

    def clear_effect(self):
        current_time = time.time()
        
        # 유효한 효과만 유지
        self.effect_end_times = [
            (end_time, effect_type) for end_time, effect_type in self.effect_end_times if end_time > current_time
        ]
        
        # 효과 스택 초기화
        self.boost_stack = sum(1 for _, effect_type in self.effect_end_times if effect_type == "boost")
        self.slow_stack = sum(1 for _, effect_type in self.effect_end_times if effect_type == "trap")
        
        # 스택을 기반으로 속도 계산
        self.max_vel = self.original_max_vel * (1.3 ** self.boost_stack) * (0.7 ** self.slow_stack)


    
    def bounce(self):
        """
        충돌 시 속도를 반전시키는 메서드
        """
        self.vel = -self.vel
        self.move()

# Player Car Class
class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (490, 10)

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 270  # 초기 각도
        self.vel = 0
        self.boosted = False
        self.slowed = False

    def __init__(self, max_vel, rotation_vel):
        super().__init__(max_vel, rotation_vel)

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 2, 0)
    
        if abs(self.vel) > 0.01:  # 속도가 낮으면 이동하지 않음
            self.move()


    def bounce(self):
        self.vel = -self.vel
        self.move()

# AI Car Class
class AICar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (490, 50)

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 270  # 초기 각도
        self.vel = 0
        self.boosted = False
        self.slowed = False

    def __init__(self, max_vel, rotation_vel, path):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0

    def update_path_point(self):
        """현재 경로 점에 도달했는지 확인하고, 다음 경로 점으로 이동"""
        if self.current_point >= len(self.path):
            return

        target_x, target_y = self.path[self.current_point]
        dist = math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)

        if dist < 20:  # 자동차가 목표 지점에 도달했으면
            self.current_point += 1

    def calculate_angle(self):
        """현재 위치에서 다음 경로 점까지의 각도 계산"""
        if self.current_point >= len(self.path):
            return 0

        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        desired_angle = math.degrees(math.atan2(y_diff, x_diff))
        angle_diff = desired_angle - self.angle

        # 각도 차이를 -180~180 범위로 제한
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        return angle_diff

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.update_path_point()
        angle_diff = self.calculate_angle()

        if angle_diff > 0:
            self.rotate(left=True)
        elif angle_diff < 0:
            self.rotate(right=True)

        # 이동 처리
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

# Draw Function
def draw(win, images, player_car, ai_car, game_info, traps, boosts):
    for img, pos in images:
        win.blit(img, pos)

    for trap in traps:
        win.blit(TRAP, trap)

    for boost in boosts:
        win.blit(BOOST, boost)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))  # 오른쪽 위로 이동

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    WIN.blit(time_text, (WIDTH - time_text.get_width() - 10, 50))  # 오른쪽 위에 정렬

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    WIN.blit(vel_text, (WIDTH - vel_text.get_width() - 10, 90))  # 오른쪽 위에 정렬


    player_car.draw(win)
    ai_car.draw(win)
    pygame.display.update()


BOOST_WIDTH, BOOST_HEIGHT = BOOST.get_width(), BOOST.get_height()
TRAP_WIDTH, TRAP_HEIGHT = TRAP.get_width(), TRAP.get_height()

# Helper function to check if item is fully inside the track
def is_item_inside_track(x, y, width, height):
    """
    아이템의 전체 영역이 도로 내부에 있는지 확인
    :param x: 아이템 중심의 x 좌표
    :param y: 아이템 중심의 y 좌표
    :param width: 아이템의 너비
    :param height: 아이템의 높이
    """
    half_width, half_height = width // 2, height // 2

    # 아이템의 각 모서리 좌표 확인
    corners = [
        (x - half_width, y - half_height),  # 왼쪽 상단
        (x + half_width, y - half_height),  # 오른쪽 상단
        (x - half_width, y + half_height),  # 왼쪽 하단
        (x + half_width, y + half_height),  # 오른쪽 하단
    ]

    # 모든 모서리가 도로 내부에 있어야 함
    for corner_x, corner_y in corners:
        try:
            if TRACK_MASK.get_at((int(corner_x), int(corner_y))) != 1:
                return False
        except IndexError:
            return False  # 경계 밖이면 False 반환
    return True

# Generate random positions for items inside the track
def generate_random_positions(count, width, height):
    """
    도로 내부에 아이템 전체가 포함되도록 무작위 좌표를 생성
    :param count: 생성할 좌표의 개수
    :param width: 아이템의 너비
    :param height: 아이템의 높이
    """
    positions = []
    attempts = 0

    while len(positions) < count and attempts < 1000:
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)

        if is_item_inside_track(x, y, width, height):
            positions.append((x, y))

        attempts += 1

    if len(positions) < count:
        print(f"Warning: Only {len(positions)} positions generated out of {count}")
    return positions


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
            if isinstance(car, PlayerCar):
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


# Main Functionality
run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

# Adjust player and AI car speeds here
player_car = PlayerCar(max_vel=4, rotation_vel=6)  # 플레이어 차량 속도 조정
ai_car = AICar(max_vel=4, rotation_vel=6, path=[(200, 200), (300, 300), (400, 200), (300, 100)])  # AI 차량 속도 조정
game_info = GameInfo()

# Generate item positions
traps = generate_random_positions(5, TRAP_WIDTH, TRAP_HEIGHT)
boosts = generate_random_positions(5, BOOST_WIDTH, BOOST_HEIGHT)


# Debugging: Visualize item positions
for pos in traps:
    WIN.set_at(pos, (255, 0, 0))  # 트랩 위치를 빨간 점으로 표시
for pos in boosts:
    WIN.set_at(pos, (0, 255, 0))  # 부스트 위치를 초록 점으로 표시
pygame.display.update()

while run:
    clock.tick(FPS)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    if time.time() >= player_car.effect_end_time:
        player_car.clear_effect()

    draw(WIN, images, player_car, ai_car, game_info, traps, boosts)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 창을 닫는 이벤트
                run = False
                pygame.quit()
                exit()  # 완전히 프로그램을 종료합니다.
        
            if event.type == pygame.KEYDOWN:  # 키 입력 감지
                game_info.start_level()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)
    ai_car.move()

    # Check for trap collision
    for trap in traps:
        if player_car.collide(pygame.mask.from_surface(TRAP), *trap):
            traps.remove(trap)
            traps.append(random.choice(generate_random_positions(1, TRAP_WIDTH, TRAP_HEIGHT)))
            player_car.apply_effect("trap")
            break

    # Check for boost collision
    for boost in boosts:
        if player_car.collide(pygame.mask.from_surface(BOOST), *boost):
            boosts.remove(boost)
            boosts.append(random.choice(generate_random_positions(1, BOOST_WIDTH, BOOST_HEIGHT)))
            player_car.apply_effect("boost")
            break

    # 플레이어와 AI 충돌 처리
    handle_collision(player_car, game_info, opponent_car=ai_car)
    handle_collision(ai_car, game_info, opponent_car=player_car)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        ai_car.reset()

pygame.quit()