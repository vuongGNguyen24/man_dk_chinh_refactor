import json
from pathlib import Path
from typing import Iterable, Union, List

from domain.models.module import Module
from domain.value_objects.parameter import Parameter, Threshold
from domain.ports.module_query_port import ModuleQueryPort


class JsonModuleQueryAdapter(ModuleQueryPort):
    """
    Outbound Adapter:
    Load Module definitions cho một Node từ JSON legacy
    """

    def __init__(self, module_config_path: Union[str, Path], node_modules_mapping_path: Union[str, Path]):
        self._module_config_path = Path(module_config_path)
        self._node_modules_mapping_path = Path(node_modules_mapping_path)

        if not self._path.exists():
            raise FileNotFoundError(f"Module config not found: {self._path}")

        self._module_configs = self._load_json(self._module_config_path)
        self._node_modules_mapping = self._load_json(self._node_modules_mapping_path)

    def load_modules_for_node(self, node_name: str) -> Iterable[Module]:
        module_configs = self._module_configs
        node_modules = self._node_modules_mapping

        if node_name not in node_modules:
            return []

        modules: List[Module] = []

        for module_name in node_modules[node_name]:
            cfg = module_configs[module_name]

            thresholds = self._build_thresholds(cfg)
            module = Module(
                module_id=cfg["id"],
                name=module_name,
                thresholds=thresholds,
            )

            self._init_default_parameters(module, cfg)
            modules.append(module)

        return modules

    # ----------------- helpers -----------------

    def _load_json(self, path: Path) -> dict:
        with self._path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_thresholds(self, cfg: dict) -> dict[str, Threshold]:
        """
        Merge default_thresholds + custom_thresholds
        (custom override default)
        """
        thresholds: dict[str, Threshold] = {}

        default = cfg.get("default_thresholds", {})
        custom = cfg.get("custom_thresholds", {})

        merged = {**default, **custom}

        for name, th in merged.items():
            thresholds[name] = Threshold(
                min_normal=th["min_normal"],
                max_normal=th["max_normal"],
                unit=th.get("unit"),
            )

        return thresholds

    def _init_default_parameters(self, module: Module, cfg: dict):
        defaults = cfg.get("default_parameters", {})

        for name, value in defaults.items():
            param = Parameter(
                name=name,
                value=value,
            )
            module.update_parameter(param)
