from abc import ABC, abstractmethod
import gym

class NormViolation(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def as_string(self):
        pass

    def __str__(self):
        return self.as_string()


class Norm(ABC):
    def __init__(self):
        self.known_violations = set()

    def preprocess(self, game, action):
        pass

    @abstractmethod
    def monitor(self, game, action):
        pass

    def reset(self):
        self.known_violations = set()


class NormWrapper(gym.Wrapper):
    def __init__(self, env, norms):
        super(NormWrapper, self).__init__(env)
        self.norms = list(norms)
        self.violations = set()

    def step(self, action):
        for norm in self.norms:
            norm.preprocess(self.env.game, action)
        obs, reward, done, info = self.env.step(action)
        violations = set()
        for norm in self.norms:
            violations.update(norm.monitor(self.env.game, action))
        self.violations = violations
        new_obs = obs
        # new_obs = {'violations': violations, 'obs': obs}
        return new_obs, reward, done, info

    def render(self, mode='human', **kwargs):
        self.env.render(mode, **kwargs)
        for violation in self.violations:
            print(violation)
        self.violations = set()

    def reset(self):
        super(NormWrapper, self).reset()
        for norm in self.norms:
            norm.reset()
