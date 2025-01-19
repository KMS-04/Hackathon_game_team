# train_dqn.py
import torch
from racing_env import RacingEnv
from dqn_agent import DQNAgent

def train_dqn(num_episodes=500):
    # 학습 시엔 보통 render_mode=False (빠른 속도로 돌리기 위해)
    env = RacingEnv(render_mode=False)

    state_dim = env.observation_space.shape[0]  # 5
    action_dim = env.action_space.n            # 4
    agent = DQNAgent(state_dim, action_dim)

    for ep in range(num_episodes):
        state = env.reset()
        done = False
        total_reward = 0.0

        while not done:
            action = agent.select_action(state)
            next_state, reward, done, info = env.step(action)

            agent.store_transition(state, action, reward, next_state, float(done))
            agent.update()

            state = next_state
            total_reward += reward

        agent.decay_epsilon()
        agent.update_target_network()

        print(f"Episode {ep+1}, Reward: {total_reward:.2f}, Eps: {agent.eps:.3f}")

    torch.save(agent.q_network.state_dict(), "racing_dqn.pth")
    print("Training finished and saved model: racing_dqn.pth")

if __name__ == "__main__":
    train_dqn()
