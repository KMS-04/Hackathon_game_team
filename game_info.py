import time

class GameInfo:
    LEVELS = 3
    MIN_DISTANCE = 5000  # 최소 이동 거리 (픽셀)
    MIN_TIME = 20        # 최소 경과 시간 (초)

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
        :return: 조건 충족 여부 (bool)
        """
        if not self.started:
            return False

        # 경과 시간 체크
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
