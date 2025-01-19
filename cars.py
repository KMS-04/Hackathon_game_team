import pygame
import math
import time

from utils import blit_rotate_center

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
        self.slow_stack = 0   # 감속 효과 누적 횟수
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
        
        # 효과 스택 다시 계산
        self.boost_stack = sum(1 for _, effect_type in self.effect_end_times if effect_type == "boost")
        self.slow_stack = sum(1 for _, effect_type in self.effect_end_times if effect_type == "trap")
        
        # 스택을 기반으로 속도 재계산
        self.max_vel = self.original_max_vel * (1.3 ** self.boost_stack) * (0.7 ** self.slow_stack)

    def bounce(self):
        """
        충돌 시 속도를 반전시키는 메서드
        """
        self.vel = -self.vel
        self.move()
    
    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 2, 0)

        if abs(self.vel) > 0.01:
            self.move()


class PlayerCar(AbstractCar):
    IMG = None  # 실제 이미지는 main에서 로드 후 클래스 속성에 할당
    START_POS = (490, 10)

    def __init__(self, max_vel, rotation_vel):
        super().__init__(max_vel, rotation_vel)

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 270  # 초기 각도
        self.vel = 0
        self.boosted = False
        self.slowed = False

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


class AICar(AbstractCar):
    IMG = None  # 실제 이미지는 main에서 로드 후 클래스 속성에 할당
    START_POS = (490, 50)

    def __init__(self, max_vel, rotation_vel, path):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 270  # 초기 각도
        self.vel = 0
        self.boosted = False
        self.slowed = False
        self.current_point = 0

    def update_path_point(self):
        """현재 경로 점에 도달했는지 확인 후, 다음 경로 점으로 이동"""
        if self.current_point >= len(self.path):
            return

        target_x, target_y = self.path[self.current_point]
        dist = math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)

        if dist < 20:  # 자동차가 목표 지점에 가까워졌으면
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
