import time

def apply_effects(car, effect_type):
    end_time = time.time() + 3
    car.effects.append((effect_type, end_time))

def clear_effects(car):
    current_time = time.time()
    car.effects = [
        (effect_type, end_time) for effect_type, end_time in car.effects if end_time > current_time
    ]

    boost_count = sum(1 for effect, _ in car.effects if effect == "boost")
    trap_count = sum(1 for effect, _ in car.effects if effect == "trap")

    car.max_vel = car.original_max_vel * (1.3 ** boost_count) * (0.7 ** trap_count)
