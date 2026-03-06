from abc import ABC, abstractmethod
from typing import List, Tuple
from domain.value_objects import BulletStatus


class LauncherInputPort(ABC):

    @abstractmethod
    def subscribe(self, callback):
        pass
