from abc import ABC, abstractmethod
from typing import List
from domain.value_objects.bullet_status import BulletStatus


class FiringStatusOutputPort(ABC):

    @abstractmethod
    def on_bullet_status_changed(self, statuses: List[BulletStatus]) -> None:
        pass