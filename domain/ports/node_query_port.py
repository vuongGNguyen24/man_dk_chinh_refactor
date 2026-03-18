from abc import ABC, abstractmethod
from typing import Iterable
from domain.models.node import Node


class NodeQueryPort(ABC):
    """
    Input Port: cung cấp danh sách các Node cần giám sát
    (nguồn có thể là file JSON, DB, CAN config, hardcode, v.v.)
    """

    @abstractmethod
    def load_nodes(self) -> Iterable[Node]:
        """
        Trả về danh sách Node (chưa hoặc đã gắn module)
        """
        pass
