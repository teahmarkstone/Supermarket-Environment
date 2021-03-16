from abc import ABC, abstractmethod

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

    @abstractmethod
    def monitor(self, game):
        pass

    def reset(self):
        self.known_violations = set()