# items.py
import random
from constants import TRACK_MASK, WIDTH, HEIGHT, TRAP, BOOST

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