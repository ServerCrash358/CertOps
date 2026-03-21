import logging
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

class RemediationEnv:
    """Simulated environment for RL training."""

    def __init__(self):
        self.state = None
        self.steps = 0
        self.max_steps = 10

    def reset(self) -> Dict:
        """Reset environment to random initial state."""
        self.state = {
            'cpu': random.uniform(40, 95),
            'memory': random.uniform(30, 90),
            'latency': random.uniform(100, 1000),
            'pods': random.randint(2, 10),
            'incident_type': random.choice(['cpu_high', 'memory_high', 'crash_loop'])
        }
        self.steps = 0
        return self.state.copy()

    def step(self, action: str) -> Tuple[Dict, float, bool]:
        """Execute action, return (new_state, reward, done)."""
        self.steps += 1

        # Simulate action effect
        if action == 'scale_up':
            self.state['pods'] += 2
            self.state['cpu'] *= 0.6
            self.state['latency'] *= 0.7
        elif action == 'scale_down':
            self.state['pods'] = max(1, self.state['pods'] - 1)
            self.state['cpu'] *= 1.3
        elif action == 'restart':
            self.state['latency'] *= 1.2  # Temporary spike
            self.state['cpu'] *= 0.9
        elif action == 'no_op':
            self.state['cpu'] *= 1.1  # Gradual degradation

        # Calculate reward
        reward = self._calculate_reward()
        done = self.steps >= self.max_steps or self._is_healthy()

        return self.state.copy(), reward, done

    def _calculate_reward(self) -> float:
        """Reward is based on system health."""
        cpu_ok = 1.0 if self.state['cpu'] < 70 else -0.5
        memory_ok = 1.0 if self.state['memory'] < 80 else -0.3
        latency_ok = 1.0 if self.state['latency'] < 300 else -0.5

        return cpu_ok + memory_ok + latency_ok - (self.steps * 0.1)  # Penalize time

    def _is_healthy(self) -> bool:
        """Check if system is healthy."""
        return (self.state['cpu'] < 70 and
                self.state['memory'] < 80 and
                self.state['latency'] < 300)


class RemediationRLAgent:
    """Q-learning agent for remediation policies."""

    def __init__(self, learning_rate: float = 0.1, discount: float = 0.95):
        self.lr = learning_rate
        self.discount = discount
        self.epsilon = 0.3  # Exploration rate

        # Q-table: state -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )

        self.actions = ['scale_up', 'scale_down', 'restart', 'no_op']

    def _discretize_state(self, state: Dict) -> str:
        """Convert continuous state to discrete buckets."""
        cpu_bucket = int(state['cpu'] / 20) * 20
        mem_bucket = int(state['memory'] / 20) * 20
        lat_bucket = int(state['latency'] / 200) * 200
        return f"{state['incident_type']}_{cpu_bucket}_{mem_bucket}_{lat_bucket}"

    def choose_action(self, state: Dict, training: bool = True) -> str:
        """Choose action using epsilon-greedy policy."""
        state_key = self._discretize_state(state)

        if training and random.random() < self.epsilon:
            return random.choice(self.actions)

        # Choose best known action
        q_values = self.q_table[state_key]
        if not q_values:
            return random.choice(self.actions)

        return max(q_values.items(), key=lambda x: x[1])[0]

    def learn(self, state: Dict, action: str, reward: float, next_state: Dict):
        """Update Q-value based on experience."""
        state_key = self._discretize_state(state)
        next_key = self._discretize_state(next_state)

        current_q = self.q_table[state_key][action]

        # Max Q-value for next state
        next_q = max(self.q_table[next_key].values()) if self.q_table[next_key] else 0

        # Q-learning update
        new_q = current_q + self.lr * (reward + self.discount * next_q - current_q)
        self.q_table[state_key][action] = new_q

    def train(self, episodes: int = 1000) -> List[float]:
        """Train agent for N episodes."""
        env = RemediationEnv()
        episode_rewards = []

        logger.info(f"Training RL agent for {episodes} episodes...")

        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            done = False

            while not done:
                action = self.choose_action(state, training=True)
                next_state, reward, done = env.step(action)
                self.learn(state, action, reward, next_state)
                total_reward += reward
                state = next_state

            episode_rewards.append(total_reward)

            # Decay exploration
            if episode % 100 == 0:
                self.epsilon = max(0.05, self.epsilon * 0.95)
                avg_reward = sum(episode_rewards[-100:]) / min(100, len(episode_rewards))
                logger.info(f"Episode {episode}: avg_reward={avg_reward:.2f}, epsilon={self.epsilon:.2f}")

        logger.info("RL training complete")
        return episode_rewards

    def get_policy(self, state: Dict) -> Dict[str, Any]:
        """Get learned policy for a state."""
        state_key = self._discretize_state(state)
        q_values = dict(self.q_table[state_key])

        if not q_values:
            return {"action": "scale_up", "confidence": 0.0, "exploration": True}

        best_action = max(q_values.items(), key=lambda x: x[1])

        # Calculate confidence as softmax-ish probability
        exp_q = {a: 2.718 ** v for a, v in q_values.items()}
        total = sum(exp_q.values())
        probs = {a: v/total for a, v in exp_q.items()}

        return {
            "action": best_action[0],
            "q_value": best_action[1],
            "confidence": probs[best_action[0]],
            "action_distribution": probs
        }


# Global agent
_rl_agent: RemediationRLAgent = None

def get_rl_agent() -> RemediationRLAgent:
    """Get or create RL agent."""
    global _rl_agent
    if _rl_agent is None:
        _rl_agent = RemediationRLAgent()
        # Pre-train if no policy exists
        _rl_agent.train(episodes=500)
    return _rl_agent
