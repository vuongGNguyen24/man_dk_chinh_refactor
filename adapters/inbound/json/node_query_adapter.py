import json
from pathlib import Path
from typing import Iterable, Union

from domain.models.node import Node
from domain.ports.node_query_port import NodeQueryPort
from infrastructure.can.can_node_registry import CanNodeRegistry

class JsonNodeQueryAdapter(NodeQueryPort):
    """
    Outbound Adapter:
    Load Node definitions từ file JSON legacy
    """

    def __init__(
        self,
        json_path: Union[str, Path],
        can_registry: CanNodeRegistry,
    ):
        self._path = Path(json_path)
        self._can_registry = can_registry

    def load_nodes(self) -> Iterable[Node]:
        data = self._load_json()
        node_index_mapping = data.get("node_index_mapping", {})

        nodes: list[Node] = []

        for node_key, cfg in node_index_mapping.items():
            node = Node(
                node_id=node_key,
                name=node_key,
            )
            nodes.append(node)

            if "can_id" in cfg:
                self._can_registry.register(
                    node.node_id,
                    cfg["can_id"],
                )

        return nodes

    def _load_json(self) -> dict:
        with self._path.open("r", encoding="utf-8") as f:
            return json.load(f)