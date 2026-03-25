import numpy as np

class SwarmCoordinator:
    def __init__(self, num_agents, arena_size):
        self.num_agents = num_agents
        self.arena_size = arena_size
        self.agent_positions = np.random.uniform(0, arena_size, (num_agents, 2))
        self.agent_velocities = np.random.uniform(-1, 1, (num_agents, 2))

    def update_positions(self, dt):
        self.agent_positions += self.agent_velocities * dt
        self.agent_positions = np.clip(self.agent_positions, 0, self.arena_size)

    def update_velocities(self):
        for i in range(self.num_agents):
            # Calculate the center of mass of nearby agents
            nearby_agents = [j for j in range(self.num_agents) if np.linalg.norm(self.agent_positions[i] - self.agent_positions[j]) < 5]
            center_of_mass = np.mean([self.agent_positions[j] for j in nearby_agents], axis=0)

            # Steer towards the center of mass
            self.agent_velocities[i] += 0.1 * (center_of_mass - self.agent_positions[i])

            # Limit the velocity
            self.agent_velocities[i] = np.clip(self.agent_velocities[i], -1, 1)

    def step(self, dt):
        self.update_positions(dt)
        self.update_velocities()
