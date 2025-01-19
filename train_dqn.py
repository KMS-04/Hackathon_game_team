# train_dqn.py
import torch
import numpy as np
from racing_env import RacingEnv  # <-- 본인의 환경 파일명
from dqn_agent import DQNAgent

def train_dqn(num_episodes=500, target_update_interval=10):
    env = RacingEnv(render_mode=False)  # 학습 시엔 보통 렌더링 끔
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    agent = DQNAgent(state_dim, action_dim)

    for episode in range(num_episodes):
        state = env.reset()
        done = False
        episode_reward = 0.0

        while not done:
            action = agent.select_action(state)
            next_state, reward, done, info = env.step(action)

            agent.store_transition(state, action, reward, next_state, float(done))
            agent.update()

            state = next_state
            episode_reward += reward

        # Epsilon Decay
        agent.decay_epsilon()

        # 타깃 네트워크 주기적 업데이트
        if (episode + 1) % target_update_interval == 0:
            agent.update_target_network()

        print(f"Episode {episode+1}  Reward: {episode_reward:.2f}  Eps: {agent.eps:.3f}")

    # 학습 완료 후 모델 저장
    torch.save(agent.q_network.state_dict(), "racing_dqn.pth")
    print("Training finished, saved model as racing_dqn.pth")


if __name__ == "__main__":
    train_dqn()
