# test_dqn.py
import torch
import time
import numpy as np

from racing_env import RacingEnv
from dqn_agent import DQNAgent

def test_dqn():
    env = RacingEnv(render_mode=True)  # pygame 화면 띄움
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    # DQN 에이전트 로드
    agent = DQNAgent(state_dim, action_dim)
    agent.q_network.load_state_dict(torch.load("racing_dqn.pth"))
    agent.q_network.eval()

    # 탐색 종료
    agent.eps = 0.0

    state = env.reset()
    done = False
    total_reward = 0.0

    while not done:
        action = agent.select_action(state)
        next_state, reward, done, info = env.step(action)
        total_reward += reward
        state = next_state

        # 너무 빠르면 화면이 깜빡이므로 조금 슬립
        # time.sleep(1/60)

    print(f"Test finished. Total Reward: {total_reward:.2f}")
    env.close()  # (선택) pygame 종료

if __name__ == "__main__":
    test_dqn()
