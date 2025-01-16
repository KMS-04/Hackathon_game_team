import pygame
import random

# 아래 두 전역 변수는 main.py에서 로드된 TRACK_MASK를 주입받거나,
# 혹은 여기서도 직접 로드가 가능하지만, 일반적으로는 main에서 전달받는 방식을 권장합니다.
TRACK_MASK = None  
WIDTH, HEIGHT = 0, 0

def is_item_inside_track(x, y, width, height):
    """
    아이템의 전체 영역이 도로 내부에 있는지 확인
    :param x: 아이템 중심 x 좌표
    :param y: 아이템 중심 y 좌표
    :param width: 아이템의 너비
    :param height: 아이템의 높이
    """
    half_width, half_height = width // 2, height // 2

    # 아이템 네 모서리 좌표
    corners = [
        (x - half_width, y - half_height),  # 왼쪽 상단
        (x + half_width, y - half_height),  # 오른쪽 상단
        (x - half_width, y + half_height),  # 왼쪽 하단
        (x + half_width, y + half_height),  # 오른쪽 하단
    ]

    # 모든 모서리가 도로 내부여야 함
    for corner_x, corner_y in corners:
        try:
            if TRACK_MASK.get_at((int(corner_x), int(corner_y))) != 1:
                return False
        except IndexError:
            return False  # 경계 밖이면 False 반환
    return True


def generate_random_positions(count, item_width, item_height):
    """
    도로 내부에 아이템 전체가 포함되도록 무작위 좌표를 생성
    :param count: 생성할 좌표 개수
    :param item_width: 아이템의 너비
    :param item_height: 아이템의 높이
    :return: [(x1, y1), (x2, y2), ...]
    """
    positions = []
    attempts = 0

    while len(positions) < count and attempts < 1000:
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)

        if is_item_inside_track(x, y, item_width, item_height):
            positions.append((x, y))

        attempts += 1

    if len(positions) < count:
        print(f"Warning: Only {len(positions)} positions generated out of {count}")
    return positions
