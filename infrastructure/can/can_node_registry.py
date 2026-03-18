class CanNodeRegistry:
    def __init__(self):
        self._node_to_can: dict[int, int] = {}

    def register(self, node_id: int, can_id: int):
        self._node_to_can[node_id] = can_id

    def get_can_id(self, node_id: int) -> int:
        try:
            return self._node_to_can[node_id]
        except KeyError:
            raise RuntimeError(f"Node {node_id} has no CAN mapping")
