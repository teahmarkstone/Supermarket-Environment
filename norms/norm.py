from abc import ABC, abstractmethod


class Norm(ABC):
    def __init__(self):
        self.known_instances = set()

    @abstractmethod
    def monitor(self, game):
        pass

    @abstractmethod
    def write_instance(self, instance):
        pass