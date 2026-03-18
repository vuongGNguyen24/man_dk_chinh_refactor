from abc import ABC, abstractmethod
from typing import Iterable
from domain.models.module import Module


class ModuleQueryPort(ABC):
    """
    Input Port: cung cấp danh sách Module cho một Node
    """

    @abstractmethod
    def load_modules_for_node(self, node_name: str) -> Iterable[Module]:
        """
        Args:
            node_name: tên logic của node (ví dụ 'ban_dieu_khien_1')

        Returns:
            Danh sách Module đã khởi tạo threshold, parameter
        """
        pass
